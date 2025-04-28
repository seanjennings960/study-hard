module Data

export Network, Node, Line, External, FuelGenerator, RenewableGenerator, Storage,
Storage, data_dir, Profile, Demand

using Base.Iterators


using XLSX
using EzXML
using DataFrames


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


function load_network_scenario(enet_file, profile_file, scenario_file)
    xl_enet = XLSX.readxlsx(enet_file)


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

    n =  EncoordNetwork(
        [table(xl_enet, name)
        for name in ["ENO", "LI", "TRF", "EDEM", "ESTR",
                     "WIND", "PV", "FUEL", "FGEN"]]...
    ) 
    externals = load_externals(n, external_profiles)
    lines = load_lines(n)
    nodes = load_nodes(n)
    return Network(externals, nodes, lines)
end


end


# using XLSX
# 
# enet_file = joinpath(data_dir, "enet39.xlsx")
# scenario_file = joinpath(data_dir, "scenario_events.xlsx")
# profile_file = joinpath(data_dir, "full_year_profs.prfl")
# # 
# # length(prof_map)
# # length(profiles)
# # 
# # for (ext, prof) in pairs(prof_map)
# #     println("External $ext | Profile $prof)")
# #     println("has profile data: $(haskey(profiles, prof))")
# # end
# # 
# 
# n = Data.load_network_scenario(enet_file, profile_file, scenario_file)
# 