using Revise
includet("../PSOps.jl")
using .PSOps
using JuMP


# %%

data_dir = "/Users/sean/code/study-hard/power-systems-ops/data/encoord"

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


# ############################################################################
# %% Simple Test Case
# ############################################################################
# TODO: Make this into a unit test


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

summarize(network, model)


# ############################################################################
# %% load real, bigboy data
# ############################################################################

enet_file = joinpath(data_dir, "enet39.xlsx")
scenario_file = joinpath(data_dir, "peak_demand_week_pu_esce.xlsx")
profile_file = joinpath(data_dir, "peak_demand_pu.prfl")
network = load_network_scenario(enet_file, profile_file, scenario_file)
costs = load_costs(network, techs)
println("Number of externals: $(length(network.externals))")
println("Number of nodes: $(length(network.nodes))")
println("Number of lines: $(length(network.lines))")



# ############################################################################
# %% Instantiate Capacity Expansion model
# ############################################################################


ϵ_max = 0.1
model = capacity_expansion(network, costs, ϵ_max)

# ############################################################################
# %% Run Optimization
# ############################################################################

# ############################################################################
# %% Run emissions pareto
# ############################################################################

# ϵ_max_0 = 210_000.
ϵ_max = [1_000_000_000., 210_000., 100_000., 50_000., 10_000., 5_000., 1_000., 100., 0.]
models = []

for ϵ_max_0 in ϵ_max
    println("#################################################################")
    println("# Solving with emissions = $ϵ_max_0")
    println("#################################################################")
    model = capacity_expansion(network, costs, ϵ_max_0)
    optimize!(model)
    # λ = dual(model[:c_emissions])
    # σ = dual_objective_value(model)
    push!(models, model)
    # push!(ϵ_max, ϵ_max_0)

    # This doesn't work... :<>
    # ϵ_max_0 = ϵ_max_0 + σ / λ
end


# ########################
# %% Plot Pareto Graph
# ########################
using Plots
gr()
# plotlyjs()

ϵ_max_log = copy(ϵ_max)
ϵ_max_log[1] = 420_000  # Hard-code the previously found unconstrained emission level
ϵ_max_log[end] = 0.0001
system_cost = [objective_value(model) for model in models]
dual_cost = [dual(model[:c_emissions]) for model in models]
x = ϵ_max_log
y = system_cost
p = plot(x, y;
    xlabel = "Emissions level (tonnes CO_2 / week)",
    ylabel = "Total system cost (\$)",
    label = "Total system cost",
    legend=:top, 
)
ylims!(p, 0, 1.75e9)

scatter!(p, x, y;
         label      = "Problem evaluations",
         markershape = :diamond,
         markersize  = 4,
         markercolor = :red,
         markerstrokecolor = :black)

x = ϵ_max_log
y = -dual_cost
yaxis2 = twinx()
plot!(yaxis2, x, y;
    color=:orange,
    linestyle=:dash,
    label = "Carbon Price",
    ylabel = "Carbon Price (λ_ϵ) (\$ / tonne CO2)",
)
# 
# plot(ϵ_max[2:end], system_cost[2:end];
#     xlabel = "Emissions level (tonnes CO_2 / week)",
#     ylabel = "Total system cost (\$)",
# )

# ############################################################################
# %% Generation Mix + Nameplate Capacity Mix
# ############################################################################
function group_by_tech(network::Network)
    groups = Dict()
    for e in network.externals
        if isa(e.type, Demand)
            # Skip demands cause they don't have an associated tech:
            # FIXME: just give demand a tech?
            continue
        end
            tech = e.type.tech
        if tech in keys(groups)
            push!(groups[tech], e)
        else
            groups[tech] = [e]
        end
    end
    return groups
end


function total_design_capacity(externals::Vector{<:External}, model)
    return sum(model[:p_max][e.name] for e in externals)
end

function total_design_energy_capacity(externals::Vector{<:External}, model)
    return sum(model[:e_max][e.name] for e in externals)
end


model = models[1]
g = group_by_tech(network)

nameplate_power = [
    Dict(
        tech => value(total_design_capacity(externals, model))
        for (tech, externals) in pairs(g)
    ) for model in models
]

ϵ_all = [value(emissions(network, model)) for model in models]

# %% VegaLite
using VegaLite

# df = DataFrame(Dict(
#     "Power" => [350, 100, 200, 100, 280, 150, 120, 120],
#     "emissions" => [3, 3, 2, 2, 1, 1, 1, 1],
#     "tech" => ["solar", "wind", "solar", "wind", "wind", "solar", "nuclear", "wind"]
# ))

function power_generation(external, model)
    u = value.(model[:u][external.name, :])
    return sum(max.(u, 0))
end

function iter_devices(network, models)
    # TODO: This would really be cleaner as a @join using Query.jl.
    generators = collect(filter(e -> !isa(e.type, Demand), network.externals))
    ems = [round(value(emissions(network, model) * 52 / 1e6), sigdigits=3) for model in models]
    ems = vec([em for (_, em) in Iterators.product(generators, ems)])
    tech = vec([g.type.tech for (g, _) in Iterators.product(generators, models)])
    name = vec([g.name for (g, _) in Iterators.product(generators, models)])
    nameplate_power = vec([value(model[:p_max][g.name])
                for (g, model) in Iterators.product(generators, models)])
    power_generated = vec([power_generation(g, model)
                for (g, model) in Iterators.product(generators, models)])
    

    return DataFrame(Dict(
        :emissions=> ems,
        :tech => tech,
        :nameplate_power => nameplate_power,
        :power_generated => power_generated,
        :name => name
    ))
end


df = iter_devices(network, models)
# %%

using Query

df |>
@filter(_.nameplate_power > 0.01) |>
@vlplot(
    :bar,
    x={
        "emissions:n",
        # scale={type="log"}
        title="Emissions (Million Tonnes CO2/year)"
    },
    y={
        :nameplate_power,
        title="Nameplate Power (MW)"
    },
    color=:tech,
    width=400,
    height=600
) 
# %%

df |>
@filter(_.power_generated > 0.01) |>
@vlplot(
    :bar,
    x={
        "emissions:n",
        # scale={type="log"}
        title="Emissions (Million Tonnes CO2/year)"
    },
    y={
        :power_generated,
        title="Power Generated (MWh)"
    },
    color=:tech,
    width=400,
    height=600
)


# ############################################################################
# %%  Dispatch plot
# ############################################################################

# using Statistics
# 
# by_model = groupby(df, :emissions)
# single_model = subset(by_model, :emissions => max => >(20))


function fill_between(x::AbstractVector, Y::AbstractMatrix, labels::Vector{String}; p=nothing, kwargs...)
    M, N = size(Y)
    @assert length(x) == N "length(x) ($(length(x))) must match size(Y,2) ($N)"
    @assert length(labels) == M-1 "length(labels) ($(length(labels))) must match size(Y,1)-1 ($(M-1))"

    if isnothing(p)
        p = plot() # start with an empty plot
    end
    # draw a filled band between row i and row i+1 of Y

    for i in 1:M-1
        plot!(p, x, Y[i, :];
        fillrange=Y[i+1, :],
        label=labels[i],
        kwargs...)
    end
    return p
end


function plot_dispatch(dispatch::Dict{String, Vector}, plot_order::Vector{String}, labels::Vector{String}; p=nothing)
    # plot_order = ["solar", "wind", "nuclear", "coal", "gas-cc"]
    # Pull the values out of the power dispatch variable of the base case model.
    stack = hcat([Array(dispatch[t]) for t in plot_order]...)
    n_T = size(stack, 1)
    # 
    stack = hcat(zeros(n_T, 1), stack)
    stack = transpose(stack)
    # println("Size: $(size(stack))")


    # stack = vcat(zeros(1, size(stack,2)), stack)  # Add a first row of zeros from which the fill starts.
    # stack /= 1000 # Convert MW -> GW

    p = fill_between(1:n_T, cumsum(stack, dims=1), labels, p=p)
    plot!(p;
        xlabel="Hour in Day",
        ylabel="Power output (GW)",
        grid = :both,
        minorgridy=true,
        minorticks=10,
        minorgridalpha=1
    )
    return p
end


function dispatch_by_tech(network, model)
    techs = unique([e.type.tech for e in network.externals if !isa(e.type, Demand)])
    dispatch_pos = Dict{String, Vector}()
    dispatch_neg = Dict{String, Vector}()
    for tech in techs
        X = [e.name for e in network.externals if !isa(e.type, Demand) && e.type.tech == tech]
        u = model[:u]
        d = Array(value.(sum(u[x, :] for x in X)))
        d_pos = max.(d, 0)
        d_neg = min.(d, 0)
        if tech == "bess"
            println(d_pos .* d_neg)
        end
        if any(d_pos .> 0)
            dispatch_pos[tech] = d_pos
        end
        if any(d_neg .< 0)
            dispatch_neg[tech] = d_neg
        end
    end
    return dispatch_pos, dispatch_neg
end



dispatch_pos, dispatch_neg = dispatch_by_tech(network, models[end])
plot_order = collect(keys(dispatch_pos))
labels = [
    k == "bess" ? "bess (discharge)" : k
    for k in plot_order
]
p = plot_dispatch(dispatch_pos, plot_order, labels)
plot_order = collect(keys(dispatch_neg))
labels = [
    k == "bess" ? "bess (charge)" : k
    for k in plot_order
]


plot_dispatch(dispatch_neg, plot_order, labels, p=p)

demands = hcat([e.type.d for e in network.externals if isa(e.type, Demand)]...)
println(size(demands))
total_demand = sum(demands, dims=2)

n_T = n_timesteps(network)
plot!(
    p,
    1:n_T, total_demand;
    label="Demand",
    linewidth=5,
    alpha=1
)


# %%
dispatch_neg["bess"] .* dispatch_pos["bess"]

# %%
plot_dispatch(dispatch_pos, ["gas_cc"], ["gas_cc"])
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


# #######################
# %% Emissions computation
# #######################


println(value(emissions(network, model)))




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
write_file = joinpath(data_dir, "enet39_pu.xlsx")
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