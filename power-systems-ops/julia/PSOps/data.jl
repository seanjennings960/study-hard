"""
Interoperation with SAint.
"""


using Base.Iterators
# include("network.jl")
# using .NetworkMod


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



"""
    save_network(net::EncoordNetwork,
                 template_xlsx::AbstractString,
                 outfile_xlsx::AbstractString)

Copy `template_xlsx` to `outfile_xlsx` and overwrite/insert the
worksheets that belong to the EncoordNetwork fields (`ENO`, `LI`, `TRF`, …)
with the data contained in `net`.

Returns the path of the written file.
"""
function save_network(net::EncoordNetwork,
                      template_xlsx::AbstractString,
                      outfile_xlsx::AbstractString)

    # --- 1. copy the template so we keep formatting, hidden sheets, etc. ----
    cp(template_xlsx, outfile_xlsx; force = true)

    # --- 2. Map sheet‑names → DataFrames -------------------------------
    sheetmap = Dict(
        "ENO"  => net.nodes,
        "LI"   => net.lines,
        "TRF"  => net.transformers,
        "EDEM" => net.demands,
        "ESTR" => net.storage,
        "WIND" => net.wind,
        "PV"   => net.pv,
        "FUEL" => net.fuel,
        "FGEN" => net.fuel_gen,
    )

    # --- 3. Open the copy in read‑write mode and dump each DataFrame ----
    XLSX.openxlsx(outfile_xlsx, mode = "rw") do xf
        present = Set(XLSX.sheetnames(xf))
        for (sheet_name, df) in sheetmap
            # get existing sheet or create it
            ws = sheet_name in present ? xf[sheet_name] :
                                          XLSX.addsheet!(xf, sheet_name)

            # Tables.columns(df) gives a Vector of column vectors
            # Tables.columnnames(df) gives the headers
            XLSX.writetable!(
                ws,
                Tables.columns(df),
                Tables.columnnames(df);
                anchor_cell = XLSX.CellRef("A1"),   # start at A1
                # overwrite   = true                  # nuke previous contents
            )                                       # :contentReference[oaicite:1]{index=1}
        end
    end

    return outfile_xlsx
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

    s = table(xl_esce, "ESCE")
    mask = .!ismissing.(s[!, "ProfileName"])

    external_name = row -> split(row["Parameter"], ".")[2]
    return Dict(
        [external_name(r) => r["ProfileName"]
         for r in eachrow(s[mask, :])]...
    )
end

# ############################################################################
# Transmission and nodes
# ############################################################################

function load_lines(network::EncoordNetwork)
    return [Line(
        l["Name"], l["FromName"], l["ToName"], 1/l["XXDEF [pu] = 0"]
    ) for l in Iterators.flatten(
        (eachrow(network.lines), eachrow(network.transformers))
    )]

end

function load_nodes(network::EncoordNetwork)
    return [Node(n["Name"]) for n in eachrow(network.nodes)]
end


# ############################################################################
# Externals
# ############################################################################


FUEL_NAME_MAP = Dict(
    "URANIUM" => "nuclear",
    "NATURAL_GAS" => "gas_cc",
    "COAL" => "coal"
)

@kwdef struct TechMap
    solar::String
    wind::String
    storage::String
end


function load_externals(network, external_profiles, tech_map::TechMap)
    # Load all the existing externals into the model. We're just going to focus
    # on the renewable/storage ones for now...
    externals = []
    e_pv = [External(
        pv["Name"], pv["NodeName"],  RenewableGenerator(
            P_max=nothing,  # Configurable
            γ=external_profiles[pv["Name"]].data,
            tech=tech_map.solar
        )
    ) for pv in eachrow(network.pv)]

    e_wind = [External(
        wind["Name"], wind["NodeName"],  RenewableGenerator(
            P_max=nothing,
            γ=external_profiles[wind["Name"]].data,
            tech=tech_map.wind
        )
    ) for wind in eachrow(network.wind)]

    e_storage = [External(
        s["Name"] * "_STORAGE", s["Name"], Storage(
            P_max=nothing, E_max=nothing,
            tech=tech_map.storage
        )
    ) for s in eachrow(network.nodes)]

    e_demand = [External(
            demand["Name"], demand["NodeName"], Demand(
            d=external_profiles[demand["Name"]].data * demand["PSETDEF [MW] = 0"]
        )
    ) for demand in eachrow(network.demands)]

    e_fgen = [External(
        fgen["Name"], fgen["NodeName"], FuelGenerator(
            P_max=nothing,
            ρ=(fgen["FuelName"] == "URANIUM") ? 1 : 0,  # Assume nuclear is always on, other have no minimum
            tech=FUEL_NAME_MAP[fgen["FuelName"]]
        )
    ) for fgen in eachrow(network.fuel_gen)]


    append!(externals, e_pv)
    append!(externals, e_wind)
    append!(externals, e_storage)
    append!(externals, e_demand)
    append!(externals, e_fgen)

    return externals
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

DEFAULT_TECHS = TechMap(
    solar="solar",
    wind="wind",
    storage="bess",
)
function load_network_scenario(enet_file, profile_file, scenario_file, tech_map::TechMap=DEFAULT_TECHS)
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

    externals = load_externals(n, external_profiles, tech_map)
    lines = load_lines(n)
    nodes = load_nodes(n)
    return Network(externals, nodes, lines)
end

function load_operation_costs(enet_file)
    network = load_raw_network(enet_file)
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


# using XLSX
# using .Data
# 
# enet_file = joinpath(data_dir, "enet39.xlsx")
# scenario_file = joinpath(data_dir, "scenario_events.xlsx")
# profile_file = joinpath(data_dir, "full_year_profs.prfl")
# 
# network = Data.load_raw_network(enet_file)
# network.pv[!, Symbol("PMAXDEF [MW] = ∞")] .= 10
# println(network.pv)
# 
# write_file = joinpath(data_dir, "enet39_best.xlsx")
# println("Writing to $write_file")
# save_network(network, enet_file, write_file)
# println("Successfully wrote file.")
# network.fuel_gen
# 

# n = Data.load_network_scenario(enet_file, profile_file, scenario_file)
# 