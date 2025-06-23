# module PSOps
# 
# export Network,
# n_timesteps, configurable_externals, configurable_energy_devices,
# configurable_power_limits, fixed_power_limits,
# Node, Line, External,
# is_configurable,
# FuelGenerator, RenewableGenerator, Storage, Demand,
# data_dir,
# # Operators
# incidence_matrix, power_transfer_distribution_matrix, bus_injection_matrix,
# energy_configuration_matrix, differential_op,
# # External interface (it's kinda weird that you have to export all of these individually,
# # unlike methods of a Python Object)
# upper_config_limit, upper_power_limit, lower_config_limit, lower_power_limit

using LinearAlgebra
using SparseArrays
using Parameters


# ############################################################################
# Parse Network into Built-in types -- so we know what we're using
# The three major concepts within my DCOPT framework are Externals (should
# really just be called generators...), Network=(Generators, Nodes, Lines)
#
# ############################################################################

@kwdef struct FuelGenerator
    P_max::Union{Nothing,Float64}  # Power capacity, or none if it is configurable
    ρ::Float64  # Minimum power ratio (P_min = ρP_max)
    tech::String
    convention::Int32=1
end
@kwdef struct RenewableGenerator
    P_max::Union{Nothing,Float64}  # Power capacity, or none if it is configurable
    γ::Vector{Float64}  # Representing PU availability across time
    tech::String
    convention::Int32=1
end
@kwdef struct Storage;
    P_max::Union{Nothing,Float64}  # Power capacity, or none if it is configurable
    E_max::Union{Nothing,Float64}  # Energy capacity, or none if configurable
    convention::Int32=1
    tech::String="bess"
end
@kwdef struct Demand;
    d::Vector{Float64}  # Representing demand at each time in units of power.
    convention::Int32=-1
end



struct External{T<:Union{FuelGenerator, RenewableGenerator, Storage, Demand}}
    name::String
    node::String
    type::T
end

###############################################################################
# External Configurability
###############################################################################

# Each External has a set of configuration parameters which can be optimized.
# For now, we have "configurability" as a property of the external as a whole.
# We might want to consider this on a per-parameter basis in the future.

function is_configurable(
    external::External{T}
    ) where T<:Union{FuelGenerator, RenewableGenerator}
    return isnothing(external.type.P_max)
end

function is_configurable(external::External{Storage})
    P_config = isnothing(external.type.P_max)
    E_config = isnothing(external.type.E_max)
    @assert sum([P_config, E_config]) != 1 "Storage's P_max and E_max cannot be configured individually."
    return P_config || E_config
end

function is_configurable(_::External{Demand})
    return false
end

###############################################################################
# Upper and Lower Power Limits
###############################################################################
# Here we make the assumption of affine lower and upper bounds on the external's
# power output. Each limit is a vector along the time axis, representing
# bounds at a given time.


function upper_config_limit(_::External{T}, n_T) where T<:Union{FuelGenerator, Storage}
    return ones(n_T)
end

function upper_config_limit(external::External{RenewableGenerator}, n_T)
    return external.type.γ
end

function lower_config_limit(external::External{FuelGenerator}, n_T)
    return [external.type.ρ for _ in 1:n_T]
end

function lower_config_limit(_::External{RenewableGenerator}, n_T)
    return zeros(n_T)
end

function lower_config_limit(_::External{Storage}, n_T)
    # Note this one is redundant with the storage-specific configs coming later...
    return -ones(n_T)
end

function lower_power_limit(_::External{RenewableGenerator}, n_T)
    return zeros(n_T)
end

function lower_power_limit(_::External{Storage}, n_T)
    return zeros(n_T)
end

function lower_power_limit(external::External{Demand}, n_T)
    return external.type.d
end

function lower_power_limit(external::External{FuelGenerator}, n_T)
    if is_configurable(external)
        return zeros(n_T)
    end
    e = external
    return e.ρ * e.P_max * ones(n_T)
end

function upper_power_limit(external::External{Demand}, n_T)
    return external.type.d
end

function upper_power_limit(external::External{FuelGenerator}, n_T)
    if is_configurable(external)
        return zeros(n_T)
    end
    return external.P_max * ones(n_T)
end

function upper_power_limit(external::External{Storage}, n_T)
    if is_configurable(external)
        return zeros(n_T)
    end
    return external.P_max * ones(n_T)
end

function upper_power_limit(external::External{RenewableGenerator}, n_T)
    if is_configurable(external)
        return zeros(n_T)
    end
    return external.type.P_max * external.type.γ  / 100  # Convert percentage to fraction.
end



# Convert lines to a simpler format: all we care about is the impedance
# and which nodes it connects.
struct Line
    name::String
    from::String
    to::String
    B::Float64  # Susceptance
end

struct Node
    name::String
end


struct Network
    externals::Vector{External}
    nodes::Vector{Node}
    lines::Vector{Line}
end

function n_timesteps(network::Network)
    i = findfirst(e -> isa(e.type, Demand), network.externals)
    # We're just going to assume all timesteps are the same, for now..
    return length(network.externals[i].type.d)
end


function fixed_power_limits(network::Network)
    n_T = n_timesteps(network)
    p_lower = vcat(
        [transpose(lower_power_limit(external, n_T)) for external in network.externals]...
    )
    p_upper = vcat(
        [transpose(upper_power_limit(external, n_T)) for external in network.externals]...
    )
    return p_lower, p_upper
end


function external_by_name(network, name)
    i = findfirst(e -> e.name == name, network.externals)
    return network.externals[i]
end



function configurable_externals(network)
    return [
        external.name
        for external in network.externals
        if is_configurable(external)
    ]
end

function configurable_energy_devices(network)
    batteries = [e for e in network.externals if isa(e.type, Storage)]
    return [b.name for b in batteries if is_configurable(b)]
end

function configurable_power_limits(network)
    X = [x.name for x in network.externals]
    C = configurable_externals(network)
    n_C = length(C)
    n_T = n_timesteps(network)
    B = [x.name for x in network.externals if isa(x.type, Storage)]

    Φ_1 = Dict(x_name => spzeros(n_T, n_C) for x_name in X)
    Φ_2 = Dict(x_name => spzeros(n_T, n_C) for x_name in X)
    Φ_4 = Dict(b_name => spzeros(n_T, n_C) for b_name in B)


    for (i, x) in enumerate(X)
        external = network.externals[i]
        if !is_configurable(external)
            continue
        end

        j = findfirst(name -> name == x, C)

        lower = lower_config_limit(external, n_T)
        upper = upper_config_limit(external, n_T)
        Φ_1[x][:, j] = lower
        Φ_2[x][:, j] = upper
        if isa(external.type, Storage)
            Φ_4[x][:, j] = upper
        end
    end

    return (C, Φ_1, Φ_2, Φ_4)
end


######################################################################################
# Useful operators for Network
######################################################################################



function energy_configuration_matrix(network::Network)
    batteries = [e for e in network.externals if isa(e.type, Storage)]
    B = [b.name for b in batteries]
    C_E = [b.name for b in batteries if is_configurable(b)]
    # Configuration matrix
    Φ_3 = spzeros(length(B), length(C_E))
    for (j, configurable) in enumerate(C_E)
        i = findfirst(n -> n == configurable, B)
        Φ_3[i, j] = 1
    end
    return Φ_3
end

function bus_injection_matrix(network::Network)
    N = [n.name for n in network.nodes]
    n_N = length(network.nodes)
    n_X = length(network.externals)
    Ψ = spzeros(n_N, n_X)
    for (x, ext) in enumerate(network.externals)
        n = findfirst(node_name -> node_name == ext.node, N)
        Ψ[n, x] = ext.type.convention
    end
    return Ψ
end

function incidence_matrix(network::Network)
    N = [n.name for n in network.nodes]

    n_N = length(N)
    n_L = length(network.lines)
    A = spzeros(n_L, n_N)
    for (i, l) in enumerate(network.lines)
        j = findfirst(n -> n == l.to, N)
        A[i, j] = -1
        k = findfirst(n -> n == l.from, N)
        A[i, k] = 1
    end
    return A
end

function power_transfer_distribution_matrix(network::Network)
    A = incidence_matrix(network)
    B = Diagonal([l.B for l in network.lines])
    # Remember: The impedance matrix
    # Y = A^T B A
    # always has an eigenvalue of 0 corresponding to
    # the vector of ones.
    return B * A * pinv(Matrix(transpose(A) * B * A))
end

######################################################################################
# Useful mathematical operators
######################################################################################
function differential_op(T)
    D = spzeros(T-1, T)
    for t in 1:T-1
        D[t, t] = -1
        D[t, t+1] = 1
    end
    return D
end

######################################################################################
# Costs
######################################################################################

@with_kw struct Technology
    capital_cost::Float64  #  $/kW
    fixed_om::Float64  # $/kW-year
    variable_om::Float64  # $/MWh
    nox::Float64=0. #  lb/MMBtu
    so2::Float64=0. #  lb/MMBtu
    co2::Float64=0. #  lb/MMBtu
    lifetime::Float64   # Years
end

struct LinearCost
    C0::Dict{String, Float64}  # External name -> Capital cost (of power)
    C1::Dict{String, Float64}  # External name -> Marginal cost (of power)
    C0_E::Dict{String, Float64}  # External name -> Capital cost of energy
    # C1_E::Dict{String, Float64}  # External name -> Marginal cost of energy
end

function load_costs(network::Network, techs::Dict{String, Technology}, c0_E::Float64)

    C = configurable_externals(network)
    C_E = configurable_energy_devices(network)

    tech_map = Dict(
        name => techs[external_by_name(network, name).type.tech]
        for name in C
    )

    C0 = Dict(
        name => tech.capital_cost / tech.lifetime + tech.fixed_om
        for (name, tech) in pairs(tech_map)
    )   # $/kW/year
    C1 = Dict(
        name => tech.variable_om
        for (name, tech) in pairs(tech_map)
    )  # $/MWh
    C0_E = Dict(
        # FIXME: Make cost of energy technology-specific.
        name => c0_E for name in C_E   # $/kWh
    )  # $/kWh/year
    return LinearCost(C0, C1, C0_E)

end



