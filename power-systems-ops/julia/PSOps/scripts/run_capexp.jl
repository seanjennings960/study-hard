using Revise
includet("../PSOps.jl")
using .PSOps
using JuMP


# %%

data_dir = "/Users/sean/code/study-hard/power-systems-ops/data"
encoord_dir = joinpath(data_dir, "encoord")

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

C0_E = 0.
enet_file = joinpath(encoord_dir, "enet39.xlsx")
scenario_file = joinpath(encoord_dir, "peak_demand_week_pu_esce.xlsx")
profile_file = joinpath(encoord_dir, "peak_demand_pu.prfl")
network = load_network_scenario(enet_file, profile_file, scenario_file)
costs = load_costs(network, techs, C0_E)
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

result_dir = joinpath(data_dir, "jump_models", "no_energy_costs")

mkdir(result_dir)

# ############################################################################
# %% Run emissions pareto
# ############################################################################

# ϵ_max_0 = 210_000.
# ϵ_max = [1_000_000_000., 210_000., 100_000., 50_000., 10_000., 5_000., 1_000., 100., 0.]
ϵ_max = [1_000_000_000.]
models = []

for ϵ_max_0 in ϵ_max
    println("#################################################################")
    println("# Solving with emissions = $ϵ_max_0")
    println("#################################################################")
    model = capacity_expansion(network, costs, ϵ_max_0)
    

    solution_file = joinpath(result_dir, "model_1.sol")
    set_optimizer_attribute(
        model, "write_solution_to_file", true)
    set_optimizer_attribute(
        model, "solution_file", solution_file)

    optimize!(model)
    # λ = dual(model[:c_emissions])
    # σ = dual_objective_value(model)
    push!(models, model)
    # push!(ϵ_max, ϵ_max_0)

    # This doesn't work... :<>
    # ϵ_max_0 = ϵ_max_0 + σ / λ
end

# %% Save a model!

using DataFrames, CSV

function save(model, model_file, primal_file, dual_file)
    write_to_file(model, model_file)

    vars  = all_variables(model)
    cons  = all_constraints(model, include_variable_in_set_constraints=false)

    sol_df  = DataFrame(
        name  = [name(v) for v in vars],
        value = value.(vars),
    )

    dual_df = DataFrame(
        cname = [name(c) for c in cons],
        dual  = dual.(cons),
    )

    CSV.write(primal_file, sol_df)
    CSV.write(dual_file,    dual_df)
end


# %%  Pickle solution:
using Serialization


jls_file = joinpath(result_dir, "network_and_costs.jls")
to_save = (network, costs, ϵ_max)
serialize(jls_file, to_save)

# for (i, model) in enumerate(models)
#     model_file = joinpath(result_dir, "model_$i.lp")
#     write_to_file(model, model_file)
# end

# %%

primal_file = joinpath(result_dir, "solution.csv")
dual_file = joinpath(result_dir, "duals.csv")
model_file = joinpath(result_dir, "model.mof.json")
save(models[1], model_file, primal_file, dual_file)


# %%
length(models)


function load(model_file, primal_file)

    # model = read_from_file(lp_file)
    # model = deserialize(jls_file)
    model = read_from_file(model_file)
    set_optimizer(model, HiGHS.Optimizer)

    sol_df = CSV.read(primal_file, DataFrame)
    for row in eachrow(sol_df)
        v = variable_by_name(model, row.name)  # works even though names aren’t registered
        if isnothing(v)
            println("Can't find variable: $(row.name)")
            continue
        end
        set_start_value(v, row.value)
    end

    # optimize!(model)            # solver starts from your provided point
    return model
end

# lp_file = joinpath(result_dir, "model_1.lp")
# model_loaded = read_from_file(lp_file)
# set_optimizer(model, HiGHS.Optimizer)
# 
# sol_df = CSV.read(primal_file, DataFrame)
# 
# row = first(eachrow(sol_df))



model_loaded = load(
    joinpath(result_dir, "model.mof.json"),
    joinpath(result_dir, "solution.csv")
)
# %% Try saving and loading to JLS and then warm starting
jls_file = joinpath(result_dir, "model.jls")
serialize(jls_file, models[1])


# %%

model_loaded = load(jls_file, primal_file)

# %%
models[1]
solution_file = joinpath(result_dir, "model_1.sol")
set_optimizer_attribute(
    models[1], "write_solution_to_file", true)
set_optimizer_attribute(
    models[1], "solution_file", solution_file)
    
optimize!(models[1])