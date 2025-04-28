
include("data.jl")
using .Data
using JuMP
import HiGHS
using DataFrames
using LinearAlgebra
using SparseArrays



# ############################################################################
# %% Load data
# ############################################################################

enet_file = joinpath(data_dir, "enet39.xlsx")
scenario_file = joinpath(data_dir, "scenario_events.xlsx")
profile_file = joinpath(data_dir, "full_year_profs.prfl")
network = Data.load_network_scenario(enet_file, profile_file, scenario_file)
println("Number of externals: $(length(network.externals))")
println("Number of nodes: $(length(network.nodes))")
println("Number of lines: $(length(network.lines))")

# ############################################################################
# %% Simple Test Case
# ############################################################################

nodes = [
    Node("1"), Node("2"), Node("3")
]
lines = [
    Line("L1", "1", "2", 1),
    Line("L2", "1", "3", 1),
    Line("L3", "2", "3", 1),
]
externals = [
    External("Fuel", "1", FuelGenerator(
        P_max=nothing, ρ=0.
    )),
    External("Ren", "2", RenewableGenerator(
        P_max=nothing, γ=vcat(ones(12), zeros(12))
    )),
    External("Dem", "3", Demand(
        d=ones(24) * 100  # Constant 100 MW load
    )),
]
network = Network(externals, nodes, lines)

costs = Dict(
    "Fuel" => 5,
    "Ren" => 0,
)

# %%





struct ModelParams
    N::Vector{String}  # Set of Node Names
    E::Vector{String}  # Set of External Names
    L::Vector{String}  # Set of Line Names
    A::SparseMatrixCSC  # Incidence Matrix
    F::SparseMatrixCSC  # Power Transfer Distribution Matrix
end

function incidence_matrix(network::Data.Network)
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
    return B * A * pinv(Matrix(transpose(A) * B * A))
end

function bus_injection_matrix(network::Network)
    N = [n.name for n in network.nodes]
    n_N = length(network.nodes)
    n_X = length(network.externals)
    Ψ = spzeros(n_N, n_X)
    for (j, ext) in enumerate(network.externals)
        i = findfirst(node_name -> node_name == ext.node, N)
        Ψ[i, j] = ext.type.convention
    end
    return Ψ
end


function is_configurable(external::External{T}) where T<:Union{FuelGenerator, RenewableGenerator}
    return isnothing(external.type.P_max)
end

function is_configurable(external::External{Storage})
    P_config = isnothing(external.type.P_max)
    E_config = isnothing(external.type.E_max)
    @assert sum(P_config, E_config) != 1 "Storage's P_max and E_max cannot be configured individually."
    return P_config || E_config
end

function is_configurable(_::External{Demand})
    return false
end

function upper_config_limit(_::External{T}, n_T) where T<:Union{FuelGenerator, Storage}
    return ones(n_T)
end

function upper_config_limit(external::External{RenewableGenerator}, n_T)
    return external.type.γ
end

function lower_config_limit(external::External{FuelGenerator}, n_T)
    return [external.type.ρ for _ in 1:n_T]
end

function lower_config_limit(_::External{T}, n_T) where T<:Union{Storage, RenewableGenerator}
    return zeros(n_T)
end

function n_timesteps(network::Network)
    i = findfirst(e -> isa(e.type, Demand), network.externals)
    # We're just going to assume all timesteps are the same, for now..
    return length(network.externals[i].type.d)
end

function all_names(external::External{T}) where T<:Union{RenewableGenerator, FuelGenerator, Demand}
    return [external.name]
end

function all_names(external::External{T}) where T<:Storage
    return [external.name * "_ch", external.name * "_dch"]
end


function x_names(externals::Vector{External})
    names = [
        all_names(external) for external in externals
    ]
    return [n for n in Iterators.flatten(names)]
end


function configurable_power_limits(network)
    X = x_names(network.externals)
    C = [
        external.name
        for external in network.externals
        if is_configurable(external)
    ]

    n_X = length(X)
    n_C = length(C)
    n_T = n_timesteps(network)

    Φ_1 = [spzeros(n_T, n_C) for _ in 1:n_X]
    Φ_2 = [spzeros(n_T, n_C) for _ in 1:n_X]


    for (x, name) in enumerate(X)

        if endswith(name, "_ch")
            ext_name = name[end-2:end]
        elseif endswith(name, "_dch")
            ext_name = name[end-3:end]
        else
            ext_name = name
        end

        i = findfirst(ext -> ext.name == ext_name, network.externals)
        external = network.externals[i]
        if !is_configurable(external)
            continue
        end

        j = findfirst(name -> name == ext_name, C)

        println(external)
        lower = lower_config_limit(external, n_T)
        upper = upper_config_limit(external, n_T)
        Φ_1[x][:, j] = lower
        Φ_2[x][:, j] = upper
    end

    return (
        C, X, Φ_1, Φ_2
    )
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

function lower_power_limit(_::External{T}, n_T) where T<:Union{RenewableGenerator, Storage}
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

function upper_power_limit(external::External{T}, n_T) where T<:Union{FuelGenerator, Storage}
    if is_configurable(external)
        return zeros(n_T)
    end
    return external.P_max * ones(n_T)
end

function upper_power_limit(external::External{RenewableGenerator}, n_T)
    if is_configurable(external)
        return zeros(n_T)
    end
    return external.type.P_max * external.type.γ
end








A = incidence_matrix(network)
F = power_transfer_distribution_matrix(network)
@assert isapprox(F * [1; 0; -1], [1/3; 2/3; 1/3])

Ψ = bus_injection_matrix(network)

C, X, Φ_1, Φ_2 = configurable_power_limits(network)


T = 24
N = [n.name for n in network.nodes]
n_N = length(N)

p_lower, p_upper = fixed_power_limits(network)

function dictify(v::AbstractMatrix, X)
    return Dict(
        x => v[i, :] for (i, x) in enumerate(X)
    )
end
function dictify(v::Vector, X)
    return Dict(
        x => v[i] for (i, x) in enumerate(X)
    )
end

p_lower = dictify(p_lower, X)
p_upper = dictify(p_upper, X)
Φ_1 = dictify(Φ_1, X)
Φ_2 = dictify(Φ_2, X)


p_L_rating = 200

model = Model(HiGHS.Optimizer)
@variable(model, p[N, 1:T])
@variable(model, u[X, 1:T])
@variable(model, p_max[C] >= 0)

@constraint(model, [t=1:T], sum(p[N, t]) == 0)  # Power balance
@constraint(model, [t=1:T], Ψ * [u[x, t] for x in X] .== p[N, t])
@constraint(model, [x=X],
    p_lower[x] + Φ_1[x] * [p_max[c] for c in C] .<= u[x, 1:T]
)
@constraint(model, [x=X],
    u[x, 1:T] .<= p_upper[x] + Φ_2[x] * [p_max[c] for c in C] 
)
L = length(network.lines)
@constraint(model, [t=1:T], -p_L_rating * ones(L) <= F * p[N, t])
@constraint(model, [t=1:T],  F * p[N, t] <= p_L_rating * ones(L))


C0 = Dict(
    "Fuel" => 20_000,
    "Ren" => 00_000
)
C1 = Dict(
    "Fuel" => 5,
    "Ren" => 0
)
@objective(model, Min,
    sum(C0[c] * p_max[c] for c in C) + sum(C1[c] * sum(u[c, t] for t=1:T) for c in C)
)

optimize!(model)
model



# function extract_params(network::Network, profile::Dict{String, Profile})
#     N = [n.name for n in nodes]
# 
#     # Incidence Matrix
#     A = incidence_matrix(N, lines)
# 
#     return ModelParams(
#         N,
#         [e.name for e in externals],
#         [l.name for l in lines],
#         A, F
#     )
# end
# 
# 
# 
# p = extract_params(network, profiles)
# 
# # %%
# 
# 
# @variable()