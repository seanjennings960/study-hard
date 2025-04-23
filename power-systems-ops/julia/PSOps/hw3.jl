# %% Imports
using CSV, DataFrames, JuMP, PrettyTables
import HiGHS



# %% Load inputs from CVSs

data_dir = "/Users/sean/code/study-hard/power-systems-ops/data"
@assert ispath(data_dir) "Path does not exist!"

timeseries = CSV.read(joinpath(data_dir, "timeseries-1.csv"), DataFrame)
plant = CSV.read(joinpath(data_dir, "plant_characteristics-1.csv"), DataFrame)

# Define lifetimes manually (not given in CSV)
L = Dict(
    "nuclear" => 50,
    "coal" => 40,
    "gas-cc" => 40,
    "wind" => 25,
    "solar" => 25
)


################################################################################################
# %% Main Capacity Expansion Modeling Code
################################################################################################

function init_params(timeseries, plant, L)
    # Extract the model parameters from their raw CSV form and return them as a NamedTuple,
    # so they are easy to access later and to avoid polluting the global namespace.

    T = nrow(timeseries)
    G = plant.plant_char  # set of generator types
    L_arr = [L[g] for g=G]

    C0 = Dict(G .=> 1000 * (plant.cap_cost ./ L_arr + plant.fom_cost))  # Convert from $/kW to $/MW
    C1 = Dict(G .=> plant.vom_cost + plant.fuel_cost)
    λ = timeseries.load_MW
    η = Dict(g => ones(Float64, T) for g in G)
    η["solar"] = timeseries.solar_cf
    η["wind"] = timeseries.wind_cf

    ϵ = Dict(G .=> plant.emit_rate)

    return (; T=T, G=G, C0=C0, C1=C1, λ=λ, η=η, ϵ=ϵ)
end

function capacity_expansion_model(params::NamedTuple)
    # Initialize the capacity expansion model with all the constraints of interest.
    (; G, T, η, λ, C0, C1) = params
    
    model = Model(HiGHS.Optimizer)
    @variable(model, p[G, 1:T] >= 0)
    @variable(model, x[G] >= 0 )
    @constraint(model, [g=G, t=1:T], p[g, t] - η[g][t] * x[g] <= 0)
    @constraint(model, [t=1:T], sum(p[g, t] for g in G) == λ[t])

    if :ϵ_max in keys(params)
        # Add the emission constraint when a maximum is given.
        (; ϵ, ϵ_max) = params
        @constraint(model, c3, sum(ϵ[g] * sum(p[g,t] for t=1:T) for g=G) <= ϵ_max)
    end

    @objective(model, Min,
        sum(C0[g] * x[g] + C1[g] * sum(p[g, t] for t=1:T)
        for g in G))
    return model
end

function summarize(model, G)
    println("Termination status: $(termination_status(model))")
    println("Dual status: $(dual_status(model))")
    x = model[:x]
    println("Optimal Capacities (GW):")
    for g=G
        println("$g: $(value(x[g])/1000)")
    end
end


################################################################################################
# %% Run Optimization on Various Cases
################################################################################################

params = init_params(timeseries, plant, L)
model = capacity_expansion_model(params)

# %% Run optimization.
optimize!(model)
summarize(model, params.G)

# %% With emissions constraints
ϵ_max_list = [100e6, 10e6, 0]
emission_models = [capacity_expansion_model(
    merge(params, (; ϵ_max=ϵ))
) for ϵ in ϵ_max_list]

# %% Optimize
for (ϵ, m) in zip(ϵ_max_list, emission_models)
    println("ϵ_max = $ϵ")
    optimize!(m)
    summarize(m, params.G)
end

# %% With Lg=1
params_lg_1 = init_params(timeseries, plant, Dict(params.G .=> 1))
model_lg_1 = capacity_expansion_model(params_lg_1)
optimize!(model_lg_1)
summarize(model_lg_1, params.G)



################################################################################################
# %% Display results in tables
################################################################################################

function tabulate(G, models::Vector{Pair{String, Model}}; latex=false)
    labels = "result" => vcat(
        "objective (billion \$)",
        ["$g capacity (GW)" for g=G]
    )
    columns = vcat(
        labels,
        [k => [
            objective_value(m)/1e9,
            value.(m[:x])./1e3...
        ]
        for (k, m) in models]
    )
    df = DataFrame(columns)

    if latex
        # Output as a Latex table
        pretty_table(df, backend = Val(:latex))
    else
        println(df)
    end
end
all_models = [
    "Lg=1" => model_lg_1,
    "Base Case" => model,
    ["ϵ_max = $(ϵ/1e6)" => m for (ϵ, m) in zip(ϵ_max_list, emission_models)]...
]
tabulate(params.G, all_models, latex=true)

# %% Generate Cost table

cost_df = DataFrame(
    "Generation Type" => params.G,
    "C0 (\$/kW)" => [params.C0[g] / 1000 for g in params.G],
    "C1 (\$/MWh)" => [params.C1[g] for g in params.G])

println(cost_df)

# %% Output to Latex
pretty_table(cost_df, backend = Val(:latex))



################################################################################################
# %% Plot the dispatch stack on peak day
################################################################################################

using Plots

function fill_between(x::AbstractVector, Y::AbstractMatrix, labels::Vector{String}; kwargs...)
    M, N = size(Y)
    @assert length(x) == N "length(x) ($(length(x))) must match size(Y,2) ($N)"
    @assert length(labels) == M-1 "length(labels) ($(length(labels))) must match size(Y,1)-1 ($(M-1))"

    p = plot() # start with an empty plot
    # draw a filled band between row i and row i+1 of Y

    for i in 1:M-1
        plot!(p, x, Y[i, :];
        fillrange=Y[i+1, :],
        label=labels[i],
        kwargs...)
    end
    return p
end

# Find peak day
i = argmax(params.λ)
x = i - (i % 24)

plot_order = ["solar", "wind", "nuclear", "coal", "gas-cc"]
# Pull the values out of the power dispatch variable of the base case model.
stack = Array(value.(model[:p][plot_order, x:x+23]))
stack = vcat(zeros(1, size(stack,2)), stack)  # Add a first row of zeros from which the fill starts.
stack /= 1000 # Convert MW -> GW

p = fill_between(1:24, cumsum(stack, dims=1), plot_order)
plot!(p;
    xlabel="Hour in Day",
    ylabel="Power output (GW)",
    grid = :both,
    minorgridy=true,
    minorticks=10,
    minorgridalpha=1
)

# %% Save figure to PNG
savefig(p, "dispatch_stack.png")
