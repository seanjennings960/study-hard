module Data
export Network, Node, Line, External, FuelGenerator, RenewableGenerator, Storage,
data_dir, Profile

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
    return [
        Profile(
            prf_node["Name"], prf_node["UID"],
            read_data(prf_node), parse(Float64, prf_node["TimeStep"]))
        for prf_node in eachelement(items)
    ]
end



# ############################################################################
# Parse Network into Built-in types -- so we know what we're using 
# The three major concepts within my DCOPT framework are Externals (should
# really just be called generators...), Network=(Generators, Nodes, Lines)
# 
# ############################################################################

struct FuelGenerator; end
struct RenewableGenerator; end
struct Storage; end



struct External{T<:Union{FuelGenerator, RenewableGenerator, Storage}}
    name::String
    node::String
    type::T
end


function load_externals(network)
    # Load all the existing externals into the model. We're just going to focus
    # on the renewable/storage ones for now...
    externals = []
    e_pv = [External(
        pv["Name"], pv["NodeName"],  RenewableGenerator()
    ) for pv in eachrow(network.pv)]
    e_wind = [External(
        wind["Name"], wind["NodeName"],  RenewableGenerator()
    ) for wind in eachrow(network.wind)]
    e_storage = [External(
        s["Name"], s["NodeName"], Storage()
    ) for s in eachrow(network.storage)
    ]

    append!(externals, e_pv)
    append!(externals, e_wind)
    append!(externals, e_storage)
    # Ignoring fuel generators for now.

    return externals
end


# Convert lines to a simpler format: all we care about is the impedance
# and which nodes it connects.
struct Line
    name::String
    to::String
    from::String
    B::Float64  # Susceptance
end

function load_lines(network::EncoordNetwork)
    return [Line(
        l["Name"], l["ToName"], l["FromName"], 1/l["XXDEF [pu] = 0"]
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




function load_network(file)
    xl = XLSX.readxlsx(file)

    sheets = XLSX.sheetnames(xl)
    println("Sheets in data.xlsx: ", sheets)

    n =  EncoordNetwork(
        [table(xl, name)
        for name in ["ENO", "LI", "TRF", "EDEM", "ESTR",
                     "WIND", "PV", "FUEL", "FGEN"]]...
    ) 
    externals = load_externals(n)
    lines = load_lines(n)
    nodes = load_nodes(n)
    return Network(externals, nodes, lines)
end


end
