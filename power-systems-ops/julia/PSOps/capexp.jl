using Revise
includet("data.jl")
using .Data
using JuMP
import HiGHS
using DataFrames
using SparseArrays

# ############################################################################
# %% Utility functions
# ############################################################################

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





# ############################################################################
# %% Capacity Expansion JuMP Modeling code
# ############################################################################

struct LinearCost
    C0::Dict{String, Float64}  # External name -> Capital cost (of power)
    C1::Dict{String, Float64}  # External name -> Marginal cost (of power)
    C0_E::Dict{String, Float64}  # External name -> Capital cost of energy
    # C1_E::Dict{String, Float64}  # External name -> Marginal cost of energy
end


function capacity_expansion(network::Network, cost::LinearCost)

    # %% Matrices and whatnot
    F = power_transfer_distribution_matrix(network)
    # @assert isapprox(F * [1; 0; -1], [1/3; 2/3; 1/3])
    Ψ = bus_injection_matrix(network)
    C, Φ_1, Φ_2, Φ_4 = configurable_power_limits(network)
    # %% Sets and some housekeeping...
    T = n_timesteps(network)
    N = [n.name for n in network.nodes]
    X = [x.name for x in network.externals]
    p_lower, p_upper = fixed_power_limits(network)
    p_lower = dictify(p_lower, X)
    p_upper = dictify(p_upper, X)
    println("power_lower: $(p_lower)")
    println("power_upper: $(p_upper)")

    ########################
    # %% Model: DCOPF
    ########################
    model = Model(HiGHS.Optimizer)
    @variable(model, p[N, 1:T])
    @variable(model, u[X, 1:T])
    @variable(model, p_max[C] >= 0)

    @constraint(model, c_power_balance[t=1:T], sum(p[N, t]) == 0)  # Power balance
    @constraint(model, c_bus_injection[t=1:T], Ψ * [u[x, t] for x in X] .== p[N, t])
    @constraint(model, c_loadability_lower[x=X],
        p_lower[x] + Φ_1[x] * [p_max[c] for c in C] .<= u[x, 1:T]
    )
    @constraint(model, c_loadability_upper[x=X],
        u[x, 1:T] .<= p_upper[x] + Φ_2[x] * [p_max[c] for c in C]
    )

    ########################
    # %% Line Constraints
    ########################
    p_L_rating = 700  # MW     FIXME: Assuming constant limit for all lines!
    n_L = length(network.lines)
    @constraint(model, [t=1:T], -p_L_rating * ones(n_L) <= F * p[N, t])
    @constraint(model, [t=1:T],  F * p[N, t] <= p_L_rating * ones(n_L))

    ########################
    # %% Battery Constraints
    ########################

    batteries = [e for e in network.externals if isa(e.type, Storage)]
    B = [b.name for b in batteries]
    C_E = [b.name for b in batteries if is_configurable(b)]
    Φ_3 = energy_configuration_matrix(network)
    D = differential_op(T)

    E_fixed = [
        is_configurable(b) ? 0. : b.E_max
        for b in batteries
    ]

    η_c = 0.96
    η_d = 0.96

    @variable(model, e[B, 1:T] >= 0)
    @variable(model, e_max[C_E] >= 0)
    @variable(model, p_charge[B, 1:T])
    @variable(model, p_discharge[B, 1:T] >= 0)

    # println("Φ_3: ", size(Φ_3))
    # println("C_E: ", length(C_E))
    # println("E_fixed: ", length(E_fixed))

    @constraint(model, c1[t in 1:T],
        e[B, t] .<= E_fixed .+ Φ_3 * [e_max[c] for c in C_E])

    @constraint(model, c_energy_boundary[b in B],
        e[b, 1] <= e[b, T])  # Should have at least as much energy at the end as beginning.


    @constraint(model, c_energy_limit[t in 1:T],
        e[B, t] .<= E_fixed .+ Φ_3 * [e_max[c] for c in C_E])
    @constraint(model, [b=B],
        D * [e[b, t] for t in 1:T]  .==
            η_c * p_charge[b, 1:end-1] .- 1/η_d * p_discharge[b, 1:end-1]
    )
    @constraint(model, [b=B], u[b, 1:T] .== p_discharge[b, 1:T] .- p_charge[b, 1:T])
    @constraint(model, [b=B], p_charge[b, :] .<= p_upper[b] + Φ_4[b] * [p_max[c] for c in C])

    ########################
    # Emissions Limit
    ########################



    ########################
    # Objective
    ########################

    C0 = cost.C0
    C1 = cost.C1
    C0_E = cost.C0_E
    total_power_capital = sum(C0[c] * p_max[c] for c in C) * 1000 # $ / kW /year * MW * (1000kW/MW) == $
    total_power_operational_pre = sum(C1[c] * sum(u[c, t] for t=1:T) for c in C) * 8760 / T # $/MWh/(T hr) * MWh * (8760 hr / year)== $ FIXME: Assuming 1 hr Δ_t
    # HACK: multiple by some factor to scale operational vs capital costs -- gives a lever in comparing
    # short-term vs. long term costs
    total_power_operational = 100 * total_power_operational_pre
    total_energy_capital = sum(C0_E[b] * e_max[b] for b in B) * 1000 # $ / kWh/year * MWh * (1000kWh / MWh) == $/year
    @objective(model, Min,
        total_power_capital + total_power_operational
        + total_energy_capital
    )
    return model
end


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
        P_max=nothing, ρ=0., tech="unused"
    )),
    External("Ren", "2", RenewableGenerator(
        P_max=nothing, γ=vcat(ones(12), zeros(12)), tech="unused"
    )),
    External("Dem", "3", Demand(
        d=ones(24) * 100  # Constant 100 MW load
    )),
    External("Store", "3", Storage(
        P_max=nothing, E_max=nothing
    )),
]

network = Network(externals, nodes, lines)
cost = LinearCost(Dict(  # C0
    "Fuel" => 20_000.,
    "Ren" => 00_000.,
    "Store" => 1_000.
), Dict(  # C1
    "Fuel" => 5.,
    "Ren" => 0.,
    "Store" => 0.
), Dict(  # C1_E
    "Store" => 1_000.
))
model = capacity_expansion(network, cost)
optimize!(model)

function summarize(network, model)
    println("Termination status: $(termination_status(model))")
    println("Dual status: $(dual_status(model))")
    p = model[:p_max]
    C = [x.name for x in network.externals if is_configurable(x)]
    println("Optimal Capacities (GW):")
    for c=C
        println("$c: $(value(p[c])/1000)")
    end
end

summarize(network, model)
# println("Objective value: $(objective_value(model))")
# println("Storage Details: $(value.(p_max))")
# value.("model[:p_max])
# value.(model[:e_max])


# ############################################################################
# %% load real, bigboy data
# ############################################################################

enet_file = joinpath(data_dir, "enet39.xlsx")
scenario_file = joinpath(data_dir, "peak_demand_week_pu_esce.xlsx")
profile_file = joinpath(data_dir, "peak_demand_pu.prfl")
network = Data.load_network_scenario(enet_file, profile_file, scenario_file)
println("Number of externals: $(length(network.externals))")
println("Number of nodes: $(length(network.nodes))")
println("Number of lines: $(length(network.lines))")


# ############################################################################
# %% Let's check that fuel generators loaded ok
# ############################################################################
for external in network.externals
    println("External $(external.name): $(typeof(external.type))")
    if isa(external.type, FuelGenerator)
        println("ρ=$(external.type.ρ)")
        println("tech=$(external.type.tech)")
    end
    if isa(external.type, RenewableGenerator)
        println("tech=$(external.type.tech)")
    end
end


# ############################################################################
# %% Externals by name
# ############################################################################

function external_by_name(network, name)
    i = findfirst(e -> e.name == name, network.externals)
    return network.externals[i]
end

# ############################################################################
# %% Cost from Technologies Initialization
# ############################################################################

using Parameters


@with_kw struct Technology
    capital_cost::Float64  #  $/kW
    fixed_om::Float64  # $/kW-year
    variable_om::Float64  # $/MWh
    nox::Float64=0. #  lb/MMBtu
    so2::Float64=0. #  lb/MMBtu
    co2::Float64=0. #  lb/MMBtu
    lifetime::Float64   # Years
end

techs = Dict(
    # source: https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2025.pdf
    "solar" =>          Technology(1_502., 20.23, 0.00, 0., 0., 0., 25.),  # single axis tracking
    "nuclear" =>        Technology(8_936., 121.99, 3.19, 0., 0., 0., 50.),  # (SMR)
    "gas_cc" =>         Technology(868., 12.12, 3.41, 0.0075, 0.00, 117, 35.),  #
    "gas_ct" =>         Technology(836., 6.87, 1.24, 0.0075, 0., 117, 35.),    # Startup: 23,100
    "bess" =>           Technology(785., 40.00, 0.0, 0., 0., 0., 20.),    # (combined cost: 1,744$/kW == 436/kWh for 4hr battery -- EIA)
                                                                            # 55% of 4hr battery cost is energy (Fu, et al 2018)
                                                                            # Thus, cost of power-related components is
                                                                            #   [45% * 1744 = 785$/kW]
                                                                            # and cost of energy-related components is
                                                                            #   [55% * 436 = 240$/kWh]
                                                                            # Total is:
                                                                            #   [785$/kW + 4 hr * 240$/kWh == 1745$/kW]
                                                                            # This was of tabulating allows us to scale energy
                                                                            # and storage independently and also ensures that costs
                                                                            # are all based on estimates from the same year.
    # "bess" =>           Technology(0., 0.00, 0.0, 0., 0., 0., 20.),    # Zero cost BESS....
    "wind" =>           Technology(1_386., 38.55, 0., 0., 0., 0., 25.),
    "coal" =>           Technology(4_103., 61.60, 6.40, 0.06, 0.09, 206, 40.)  # Greenfield no carbon cap
)

function load_costs(network::Network, techs::Dict{String, Technology})

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
        # FIXME: hard-coding the bess cost here!
        # name => 240 for name in C_E   # $/kWh
        name => 0 for name in C_E   # $/kWh
    )  # $/kWh/year
    return LinearCost(C0, C1, C0_E)

end

costs = load_costs(network, techs)

# ############################################################################
# %% Instantiate Capacity Expansion model
# ############################################################################


model = capacity_expansion(network, costs)

# ############################################################################
# %% Run Optimization
# ############################################################################

# Wooooo, it works. Now we, need to see if it's doing something reasonable.
optimize!(model)


# ############################################################################
# Analysis of results
# %% Okay, we have it optimizing for the smaller problem. Let's analyze
# the results...
# ############################################################################

# #######################
# Print power capacities
# #######################

println("External | Tech | Power Capacity (MW)")
for name in configurable_externals(network)
    external = external_by_name(network, name)
    cap = value(model[:p_max][name])
    println("$(name) | $(external.type.tech) | $(cap)")
end

# #######################
# %% Print dispatch
# #######################

t_index = 150
println("External | Tech | Dispatch at t=$(t_index) Capacity (MW)")
for name in configurable_externals(network)
    external = external_by_name(network, name)
    dispatch = value(model[:u][name, t_index])
    println("$(name) | $(external.type.tech) | $(dispatch)")
end

# #######################
# %% Print energy info
# #######################

println("External | Tech | Power Capacity (MW) | Energy Capacity (MWh) | Duration (hr)")
for name in configurable_energy_devices(network)
    external = external_by_name(network, name)
    cap = value(model[:p_max][name])
    if cap < 1
        continue
    end
    e_cap = value(model[:e_max][name])
    duration = e_cap / cap
    println("$(name) | $(external.type.tech) | $(cap) | $(e_cap) | $(duration)")
end




# ############################################################################
# %% For some reason, the loadability limits are not making it through...
# Let's investigate.
# ############################################################################


ext = external_by_name(network, "PROVIDENCE_DEMAND")
profs = load_profiles(profile_file)

upper_power_limit(ext, 1)[2]
lower, upper = fixed_power_limits(network)
keys(profs)
profs["EDEM_PROVIDENCE_DEMAND_PSET"]



# ############################################################################
# %% Save Model to .enet
# ############################################################################

function filter_by_type(externals::Vector{External}, T, tech::Union{Nothing, String}=nothing)
    return filter(e -> isa(e.type, T) && (isnothing(tech) || e.type.tech == tech), externals)
end
# %%

encoord_net = load_raw_network(enet_file)

for ext in filter_by_type(network.externals, RenewableGenerator, "solar")
    i = findfirst(name -> name == ext.name, encoord_net.pv[:, "Name"])
    p_max = value(model[:p_max][ext.name])
    encoord_net.pv[i, "PMAXDEF [MW] = ∞"] = Int64(ceil(p_max))
end

println(encoord_net.pv[:, "PMAXDEF [MW] = ∞"])

for ext in filter_by_type(network.externals, RenewableGenerator, "wind")
    i = findfirst(name -> name == ext.name, encoord_net.wind[:, "Name"])
    p_max = value(model[:p_max][ext.name])
    encoord_net.wind[i, "PMAXDEF [MW] = ∞"] = Int64(ceil(p_max))
end

for ext in filter_by_type(network.externals, FuelGenerator)
    i = findfirst(name -> name == ext.name, encoord_net.fuel_gen[:, "Name"])
    p_max = value(model[:p_max][ext.name])
    encoord_net.fuel_gen[i, "PMAXDEF [MW] = ∞"] = Int64(ceil(p_max))
end

template = NamedTuple(encoord_net.storage[1, :])

rows = NamedTuple[]

for ext in filter_by_type(network.externals, Storage)
    p_max = value(model[:p_max][ext.name])
    e_max = value(model[:e_max][ext.name]) * 3600  # MWh * (3600sec/ hr) = MW-s = MJ
    if p_max < 1
        continue
    end
    # row = Dict(template)
    # row["PDMAXDEF [MW] = ∞"] = p_max
    # row["PGMAXDEF [MW] = ∞"] = p_max
    p_max = Int64(ceil(p_max))
    push!(rows, merge(template, (;
        Symbol("Name") => ext.name,
        Symbol("NodeName") => ext.node,
        Symbol("PDMAXDEF [MW] = ∞") => p_max,
        Symbol("PGMAXDEF [MW] = ∞") => p_max,
        Symbol("MaxCapDef [MJ] = ∞") => e_max
    )))
end


new_storage = DataFrame(rows, names(encoord_net.storage))

function update_storage(n::EncoordNetwork, new_storage)
    return EncoordNetwork(
        n.nodes,
        n.lines,
        n.transformers,
        n.demands,
        new_storage,
        n.wind,
        n.pv,
        n.fuel,
        n.fuel_gen
    )
end

new_network = update_storage(encoord_net, new_storage)
# new_storage[:, "PDMAXDEF [MW] = ∞"]
write_file = joinpath(data_dir, "enet39_best.xlsx")
save_network(new_network, enet_file, write_file)


# ############################################################################
# %% Plotting / Debugging
# ############################################################################
# Okay, it looks like our plots don't entirely line up with encoord's...
# The issue seems to be with the profile saving on encoord's side.
# For some reason when saving the renewable availability profile, it loads
# a large number

peak_profs = load_profiles(profile_file)
pu_profs = load_profiles(joinpath(data_dir, "just_wallingford.prfl"))

using Plots
plotlyjs()

p1 = peak_profs["PV_WALLINGFORD_PSET"].data
p2 = pu_profs["PV_WALLINGFORD_PSET_PU"].data
T1 = size(p1, 1)
T2 = size(p2, 1)
p = plot(1:T1, p1, label="PSET")
plot!(p, 1:T2, p2 * 100, label="PSET_PU (percent)")

display(p)

# gui()
# %%

new_pu_profs = load_profiles(joinpath(data_dir, "peak_demand_pu.prfl"))
p = plot()
for (name, prof) in pairs(new_pu_profs)
    if name == "PRF_WINSLOW"
        continue
    end
    T = length(prof.data)
    plot!(p, 1:T, prof.data, label=name)
end
display(p)