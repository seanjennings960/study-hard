module Data


export Network,
n_timesteps, configurable_externals, configurable_energy_devices,
Node, Line, External,
is_configurable,
FuelGenerator, RenewableGenerator, Storage, Demand,
data_dir,
# Operators
incidence_matrix, power_transfer_distribution_matrix, bus_injection_matrix,
energy_configuration_matrix,
load_network_scenario, load_operation_costs, fixed_power_limits, configurable_power_limits,
differential_op

using Base.Iterators


using XLSX
using EzXML
using DataFrames
using LinearAlgebra
using SparseArrays


data_dir = "/Users/sean/code/study-hard/power-systems-ops/data/encoord"

struct EncoordNetwork
    # Direct from Encoord
    nodes::DataFrame
    lines::DataFrame
    transformers::DataFrame
    demands::DataFrame
    storage::DataFrame
    wind::DataFrame
    pv::DataFrame
    fuel::DataFrame
    fuel_gen::DataFrame
end

function table(xlsx_file, sheet_name)
    return DataFrame(XLSX.gettable(
        xlsx_file[sheet_name];
        stop_in_empty_row=false,
        keep_empty_rows=false,
        infer_eltypes=true
    ))
end


# ############################################################################
# Read info to identify the parameters specific to DCOPF
# ############################################################################

#info = table(xl, "INFO")
#describe(info)
#info = filter(row -> begin
#    val = row[:"Applicable for Scenario Type"]
#    !ismissing(val) && occursin("DCUCOPF", val)
#end, info)

# DEADEND: not gonna look at every single parameter...

# ############################################################################
# Load profiles
# ############################################################################

struct Profile
    name::String
    UID::String
    data::Vector{Float64}
    timeStep::Float64
end

function read_data(prf_node)
    prfdata = firstelement(prf_node)
    return [parse(Float64, data["Mean"]) for data in eachelement(prfdata)]
end

function load_profiles(file::String)
    doc = readxml(file)
    items = firstelement(root(doc))
    profiles = [
        Profile(
            prf_node["Name"], prf_node["UID"],
            read_data(prf_node), parse(Float64, prf_node["TimeStep"]))
        for prf_node in eachelement(items)
    ]
    return Dict([
        p.name => p
        for p in profiles
    ])
end


function profile_map(scenario_file)
    # Map External name -> profile_name
    xl_esce = XLSX.readxlsx(scenario_file)

    s = Data.table(xl_esce, "ESCE")
    mask = .!ismissing.(s[!, "ProfileName"])

    external_name = row -> split(row["Parameter"], ".")[2]
    return Dict(
        [external_name(r) => r["ProfileName"]
         for r in eachrow(s[mask, :])]...
    )
end





# ############################################################################
# Parse Network into Built-in types -- so we know what we're using
# The three major concepts within my DCOPT framework are Externals (should
# really just be called generators...), Network=(Generators, Nodes, Lines)
#
# ############################################################################

@kwdef struct FuelGenerator
    P_max::Union{Nothing,Float64}  # Power capacity, or none if it is configurable
    ρ::Float64  # Minimum power ratio (P_min = ρP_max)
    convention::Int32=1
end
@kwdef struct RenewableGenerator
    P_max::Union{Nothing,Float64}  # Power capacity, or none if it is configurable
    γ::Vector{Float64}  # Representing PU availability across time
    convention::Int32=1
end
@kwdef struct Storage;
    P_max::Union{Nothing,Float64}  # Power capacity, or none if it is configurable
    E_max::Union{Nothing,Float64}  # Energy capacity, or none if configurable
    convention::Int32=1
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


function load_externals(network, external_profiles)
    # Load all the existing externals into the model. We're just going to focus
    # on the renewable/storage ones for now...
    externals = []
    e_pv = [External(
        pv["Name"], pv["NodeName"],  RenewableGenerator(
            P_max=nothing,  # Configurable
            γ=external_profiles[pv["Name"]].data
        )
    ) for pv in eachrow(network.pv)]

    e_wind = [External(
        wind["Name"], wind["NodeName"],  RenewableGenerator(
            P_max=nothing,
            γ=external_profiles[wind["Name"]].data
        )
    ) for wind in eachrow(network.wind)]

    e_storage = [External(
        s["Name"], s["NodeName"], Storage(
            P_max=nothing, E_max=nothing
        )
    ) for s in eachrow(network.storage)]

    e_demand = [External(
        demand["Name"], demand["NodeName"], Demand(
            d=external_profiles[demand["Name"]].data
        )
    ) for demand in eachrow(network.demands)]


    append!(externals, e_pv)
    append!(externals, e_wind)
    append!(externals, e_storage)
    append!(externals, e_demand)
    # Ignoring fuel generators for now.

    return externals
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
    return zeros(n_T, 2)
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
        return zeros(n_T, 2)
    end
    return external.P_max * ones(n_T, 2)
end

function upper_power_limit(external::External{RenewableGenerator}, n_T)
    if is_configurable(external)
        return zeros(n_T)
    end
    return external.type.P_max * external.type.γ
end



# Convert lines to a simpler format: all we care about is the impedance
# and which nodes it connects.
struct Line
    name::String
    from::String
    to::String
    B::Float64  # Susceptance
end

function load_lines(network::EncoordNetwork)
    return [Line(
        l["Name"], l["FromName"], l["ToName"], 1/l["XXDEF [pu] = 0"]
    ) for l in Iterators.flatten(
        (eachrow(network.lines), eachrow(network.transformers))
    )]

end

struct Node
    name::String
end

function load_nodes(network)
    return [Node(n["Name"]) for n in eachrow(network.nodes)]
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


function configurable_externals(network)
    return [
        external.name
        for external in network.externals
        if is_configurable(external)
    ]
end

function configurable_energy_devices(network)
    batteries = [e for e in network.externals if isa(e.type, Storage)]
    B = [b.name for b in batteries]
    return [b.name for b in batteries if is_configurable(b)]
end

function configurable_power_limits(network)
    X = [x.name for x in network.externals]
    C = configurable_externals(network)
    n_C = length(C)
    n_T = n_timesteps(network)
    B = [x.name for x in network.externals if isa(x.type, Storage)]
    n_B = length(B)

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
# Load the whole network scenario shebang
######################################################################################

function load_raw_network(enet_file)
    xl_enet = XLSX.readxlsx(enet_file)
    return  EncoordNetwork(
        [table(xl_enet, name)
        for name in ["ENO", "LI", "TRF", "EDEM", "ESTR",
                     "WIND", "PV", "FUEL", "FGEN"]]...
    )
end

function load_network_scenario(enet_file, profile_file, scenario_file)
    n = load_raw_network(enet_file)


    # Map external_names -> profile name
    prof_map = profile_map(scenario_file)
    # Map of profile names -> profiles
    profiles = load_profiles(profile_file)
    external_profiles = Dict(
        [external_name => profiles[profile_name]
         for (external_name, profile_name) in pairs(prof_map)]
    )

    # sheets = XLSX.sheetnames(xl)
    # println("Sheets in data.xlsx: ", sheets)

    externals = load_externals(n, external_profiles)
    lines = load_lines(n)
    nodes = load_nodes(n)
    return Network(externals, nodes, lines)
end

function load_operation_costs(enet_file)
    network = Data.load_raw_network(enet_file)
    C1 = Dict()
    for gen in eachrow(network.fuel_gen)
        C1[gen["Name"]] = gen["C1DEF [\$/MWh] = 0"]
    end
    for gen in eachrow(network.wind)
        C1[gen["Name"]] = 0
    end
    for gen in eachrow(network.pv)
        C1[gen["Name"]] = 0
    end
    for gen in eachrow(network.storage)
        C1[gen["Name"]] = 0
    end
    return C1
end


end


# using XLSX
#
# enet_file = joinpath(data_dir, "enet39.xlsx")
# scenario_file = joinpath(data_dir, "scenario_events.xlsx")
# profile_file = joinpath(data_dir, "full_year_profs.prfl")
#
# network = Data.load_raw_network(enet_file)
# network.fuel_gen
#
# C0 = Dict()
# #
# # for (ext, prof) in pairs(prof_map)
# #     println("External $ext | Profile $prof)")
# #     println("has profile data: $(haskey(profiles, prof))")
# # end
# #
#
# n = Data.load_network_scenario(enet_file, profile_file, scenario_file)
#