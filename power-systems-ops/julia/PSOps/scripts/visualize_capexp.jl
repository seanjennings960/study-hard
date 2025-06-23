
using Revise
includet("../PSOps.jl")
using .PSOps

using Serialization
using JuMP

# %%

data_dir = "/Users/sean/code/study-hard/power-systems-ops/data/jump_models"
result_dir = joinpath(data_dir, "no_energy_costs")
jls_file = joinpath(result_dir, "network_and_costs.jls")
network, costs, ϵ_max = deserialize(jls_file)

models = []
for i in range(1, length(ϵ_max))
    model = read_from_file(
        joinpath(result_dir, "model_$i.lp")
    )
    push!(models, model)
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

# ylims!(p, 0, 3.0e9)

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
scatter!(yaxis2, x, y;
         label      = " ",
         markershape = :diamond,
         markersize  = 4,
         markercolor = :red,
         markerstrokecolor = :black)
# 
# plot(ϵ_max[2:end], system_cost[2:end];
#     xlabel = "Emissions level (tonnes CO_2 / week)",
#     ylabel = "Total system cost (\$)",
# )

# %%
println("eps: $ϵ_max_log")
println("System: $system_cost")
println("Dual: $dual_cost")

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

function duration(external, model)
    storage_devices = [k[1] for k in keys(model[:e_max])]
    if external.name in storage_devices
        e_max = value(model[:e_max][external.name])
        p_max = value(model[:p_max][external.name])
        if p_max > 0.1
            return e_max / p_max
        else
            return 0
        end
    else
        return 0
    end
end

function iter_devices(network, models)
    # TODO: This would really be cleaner as a @join using Query.jl.
    generators = collect(filter(e -> !isa(e.type, Demand), network.externals))
    ems = [round(value(emissions(network, model) * 52 / 1e6), sigdigits=3) for model in models]
    ems = vec([em for (_, em) in Iterators.product(generators, ems)])
    tech = vec([g.type.tech for (g, _) in Iterators.product(generators, models)])
    name = vec([g.name for (g, _) in Iterators.product(generators, models)])
    node = vec([g.node for (g, _) in Iterators.product(generators, models)])
    duration_vec = vec([duration(g, model) for (g, model) in Iterators.product(generators, models)])
    nameplate_power = vec([value(model[:p_max][g.name])
                for (g, model) in Iterators.product(generators, models)])
    power_generated = vec([power_generation(g, model)
                for (g, model) in Iterators.product(generators, models)])
    

    return DataFrame(Dict(
        :emissions=> ems,
        :tech => tech,
        :nameplate_power => nameplate_power,
        :power_generated => power_generated,
        :name => name,
        :duration => duration_vec,
        :node => node
    ))
end


df = iter_devices(network, models)
nameplate_energy = df[!, "duration"] .* df[!, "nameplate_power"]
df[!, "nameplate_energy"] = nameplate_energy
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

# %%

# ############################################################################
# %%  Costs table 
# ############################################################################


# Nah...  Hold off on this for now, doesn't really add to the narative
println(keys(costs.C0))


# ############################################################################
# %%  Battery Sizes
# ############################################################################

df |>
@filter(_.power_generated > 0.01) |>
@filter(_.tech == "bess") |>
@vlplot(
    :bar,
    x = {
        "emissions:n",
        title="emissions (Million Tonnes CO2/year)",
    },
    y = {
        :nameplate_power,
        title="Nameplate Power (MW)"
        # scale={type="log"}
    },
    color=:node,
    height=500,
    width=400
)

# %%
df |>
@filter(_.power_generated > 0.01) |>
@filter(_.tech == "bess") |>
@vlplot(
    :bar,
    x = {
        "emissions:n",
        title="emissions (Million Tonnes CO2/year)",
    },
    y = {
        :nameplate_energy,
        title="Nameplate Energy (MWh)"
        # scale={type="log"}
    },
    color=:node,
    height=500,
    width=400
)


# %% Durations

out = df |>
@filter(_.power_generated > 0.01) |>
@filter(_.nameplate_energy > 0.01) |>
@filter(_.tech == "bess") |>
# @vlplot(
#     facet={
#         field=:emissions,
#         type="nominal",
#         columns=2
#     },
#     spec = {
#         @vlplot(
#             :bar,
#             x = {
#                 field="node",
#                 type="nominal",
#                 title="emissions (Million Tonnes CO2/year)",
#             },
#             y = {
#                 field=:duration,
#                 title="Duration (hr)"
#                 # scale={type="Durationlog"}
#             },
#             color=:node,
#         )
#     },
#     height=500,
#     width=400
# )
@vlplot(
    :bar,
    encoding = {
        x = {
            field="node",
            type="nominal",
            title="emissions (Million Tonnes CO2/year)",
        },
        y = {
            field=:nameplate_power,
            # title="Duration (hr)"
            scale={
                type="symlog",
                constant=1
            }
        },
        color=:node,
        facet={
            field=:emissions,
            type="nominal",
            columns=2
        },

    },
    height=500,
    width=400
)




println(out)
display(out)
# %%

using JSON

println(JSON.json(out, 2))




# ############################################################################
# %%  Dispatch plot
# ############################################################################

# using Statistics
# 
# by_model = groupby(df, :emissions)
# single_model = subset(by_model, :emissions => max => >(20))


function fill_between(x::AbstractVector, Y::AbstractMatrix, labels::Vector{String};
        p=nothing, cycle_colors=false, kwargs...)
    M, N = size(Y)
    @assert length(x) == N "length(x) ($(length(x))) must match size(Y,2) ($N)"
    @assert length(labels) == M-1 "length(labels) ($(length(labels))) must match size(Y,1)-1 ($(M-1))"

    if isnothing(p)
        p = plot() # start with an empty plot
    end
    # draw a filled band between row i and row i+1 of Y

    for i in 1:M-1
        # FIXME: there must be a better way to do this with kwargs, but it's a NamedTuple not a dict... hmm
        # if cycle_colors
        #     kwargs["color"] = i
        # end
        if cycle_colors
            plot!(p, x, Y[i, :];
            fillrange=Y[i+1, :],
            label="",
            color=i,
            kwargs...)
        else
            plot!(p, x, Y[i, :];
            fillrange=Y[i+1, :],
            label=labels[i],
            kwargs...)
        end
    end
    return p
end


function plot_dispatch(dispatch::Dict{String, Vector}, plot_order::Vector{String}, labels::Vector{String}; p=nothing, cycle_colors=false)
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

    p = fill_between(1:n_T, cumsum(stack, dims=1), labels, p=p, cycle_colors=cycle_colors)
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

# ############################################################################
# %%  Storage Dispatch
# ############################################################################

function bess_dispatch_by_node(network, model)
    p_max = value.(model[:p_max])
    bess = unique([e for e in network.externals if isa(e.type, Storage) && p_max[e.name] > 0.1])
    dispatch_pos = Dict{String, Vector}()
    dispatch_neg = Dict{String, Vector}()
    soc = Dict{String, Vector}()
    energy_max = Dict{String, Float64}()
    for external in bess
        name = external.name
        node = external.node
        d = Array(value.(model[:u][name, :]))

        d_pos = max.(d, 0)
        d_neg = min.(d, 0)

        if any(d_pos .> 0)
            dispatch_pos[node] = d_pos
        end
        if any(d_neg .< 0)
            dispatch_neg[node] = d_neg
        end
        # soc[node] = Array(value.(model[:e][name, :])) ./ value(model[:e_max][name]) * 100
        soc[node] = Array(value.(model[:e][name, :])) ./ value(model[:e_max][name]) * 100
        energy_max[node] = value(model[:e_max][name])
    end
    return dispatch_pos, dispatch_neg, soc, energy_max
end

plotlyjs()
dispatch_pos, dispatch_neg, soc, energy_max = bess_dispatch_by_node(network, models[2])

plot_order = collect(keys(dispatch_pos))
labels = plot_order
# labels = [
#     k * " (discharge)"
#     for k in plot_order
# ]
p = plot_dispatch(dispatch_pos, plot_order, labels)

plot_order = collect(keys(dispatch_neg))
labels = [
    k * " (charge)"
    for k in plot_order
]
# labels = [
#     k == "bess" ? "bess (charge)" : k
#     for k in plot_order
# ]


plot_dispatch(dispatch_neg, plot_order, labels, p=p, cycle_colors=true)



# %%
p = plot()
for (name, e_max) in pairs(energy_max)
    energy = soc[name] ./ 100 .* e_max
    n_T = length(energy)
    # println("Charge: $charge")
    plot!(p, 1:n_T, energy; label=name)
end
p


# %% ChatGPT's subplot plot

day = 0
start_hour = day * 24

# --- basic helpers ----------------------------------------------------------
keys_list = collect(keys(soc))                 # preserve insertion order
n_T        = length(first(soc)[2])                # length of a single vector
time = [t for t in 1:n_T] .- start_hour

# layout = (2, 4)                                # 2 rows × 4 cols
layout = (2, Int64(ceil(length(keys_list) / 2)))                                # 2 rows × 4 cols
plt    = plot(layout = layout, link = :both,   # link both x & y axes
              legend = false,                  # per‑subplot legends get busy
              xlabel = "Hour in day",
              ylabel = "State of charge (%)")

# --- add one series per pane -------------------------------------------------
for (i, k) in enumerate(keys_list)
    e_max = round(energy_max[k]; sigdigits=3)
    plot!(plt, time, soc[k];
          subplot = i,          # send this line to pane i
          title   = "$k ($e_max MWh)",
          titlefontsize=6)          # pane title = dictionary key
end

# if you want the empty 8‑th pane completely blank:
plot!(plt; subplot = prod(layout),
    # framestyle = :none)
)

# xlims!(plt, (0, 24))

display(plt)                    # show in REPL/notebook


# show(p)
# %%
plot_order = collect(keys(soc))
labels = plot_order
plot_dispatch(soc, plot_order, labels)


# %%
p = plot()
y = soc["WORCESTER_MA"]
plot!(p, 1:n_T, y)
y = soc["LITTLETON_MA"]
plot!(p, 1:n_T, y)




# ############################################################################
# %% Can we solve over full year in any reasonable amount of time?
# ############################################################################

enet_file = joinpath(data_dir, "enet39.xlsx")
scenario_file = joinpath(data_dir, "peak_demand_week_pu_esce.xlsx")
profile_file = joinpath(data_dir, "full_year_profs.prfl")
network_full = load_network_scenario(enet_file, profile_file, scenario_file)
# costs = load_costs(network, techs)
println("Number of externals: $(length(network.externals))")
println("Number of nodes: $(length(network.nodes))")
println("Number of lines: $(length(network.lines))")



# %%

# ############################################################################
# %% Instantiate Capacity Expansion model
# ############################################################################


ϵ_max = 0.0
model_full = capacity_expansion(network_full, costs, ϵ_max)

# %%
optimize!(model_full)
# The answer is: no, no we cannot.



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