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
# %% Simple Test Case
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
    p_L_rating = 200

    ########################
    # %% Model: DCOPF
    ########################
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

    ########################
    # %% Line Constraints
    ########################
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
    @constraint(model, c1[b in B],
        e[b, 1:T] .<= E_fixed .+ Φ_3 * [e_max[c] for c in C_E])
    @constraint(model, [b=B],
        D * [e[b, t] for t in 1:T]  .==
            η_c * p_charge[b, 1:end-1] .- 1/η_d * p_discharge[b, 1:end-1]
    )
    @constraint(model, [b=B], u[b, 1:T] .== p_discharge[b, 1:T] .- p_charge[b, 1:T])
    @constraint(model, [b=B], p_charge[b, :] .<= p_upper[b] + Φ_4[b] * [p_max[c] for c in C])

    C0 = cost.C0
    C1 = cost.C1
    C0_E = cost.C0_E
    total_power_capital = sum(C0[c] * p_max[c] for c in C)
    total_power_operational = sum(C1[c] * sum(u[c, t] for t=1:T) for c in C)
    total_energy_capital = sum(C0_E[b] * e_max[b] for b in B)
    # %% The cost of getting shit done.
    @objective(model, Min,
        total_power_capital + total_power_operational
        + total_energy_capital
    )
    return model
end


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
scenario_file = joinpath(data_dir, "scenario_events.xlsx")
profile_file = joinpath(data_dir, "full_year_profs.prfl")
network = Data.load_network_scenario(enet_file, profile_file, scenario_file)
println("Number of externals: $(length(network.externals))")
println("Number of nodes: $(length(network.nodes))")
println("Number of lines: $(length(network.lines))")


# ############################################################################
# %% run that mofo
# ############################################################################

using Parameters


@with_kw struct Technology
    capital_cost::Float64  #  $/kW
    fixed_om::Float64  # $/kW-year
    variable_om::Float64  # $/MWh
    nox::Float64=0. #  lb/MMBtu
    so2::Float64=0. #  lb/MMBtu
    co2::Float64=0. #  lb/MMBtu
end

# @kwdef struct Technologies;
#     solar::Technology
#     nuclear::Technology
#     gas_cc::Technology
#     gas_ct::Technology
#     bess::Technology
#     wind::Technology
#     coal::Technology
# end

techs = Dict(
    # source: https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2025.pdf
    "solar" =>          Technology(1_502., 20.23, 0.00, 0., 0., 0.),  # single axis tracking
    "nuclear" =>        Technology(8_936., 121.99, 3.19, 0., 0., 0.,),  # (SMR)
    "gas_cc" =>         Technology(868., 12.12, 3.41, 0.0075, 0.00, 117),  #
    "gas_ct" =>         Technology(836., 6.87, 1.24, 0.0075, 0., 117),    # Startup: 23,100
    "bess" =>           Technology(1_744., 40.00, 0.0, 0., 0., 0.), # 436/kWh
    "wind" =>           Technology(1_386., 38.55, 0., 0., 0., 0.),
    "coal" =>           Technology(4_103., 61.60, 6.40, 0.06, 0.09, 206)  # Greenfield no carbon cap
)

# tech_to_external_type = Dict(
#     "solar" => RenewableGenerator,
#     "nuclear" => FuelGenerator,
#     "gas_cc" => FuelGenerator,
#     "gas_ct" => FuelGenerator,
#     "bess" => Storage,
#     "wind" => RenewableGenerator,
#     "coal" => FuelGenerator
# )

# %%


C = configurable_externals(network)
C_E = configurable_energy_devices(network)

# FIXME: using old costs!!
C1 = load_operation_costs(enet_file)
C0 = Dict(
    name => 0 for name in C
)
C0_E = Dict(
    name => 0 for name in C_E
)
cost = LinearCost(
    C0,
    C1,
    C0_E
)
model = capacity_expansion(network, cost)

# %%
C_E
# %% okay... we have a model without too much trouble... hahaha

# Wooooo, it works. Now we, need to see if it's doing something reasonable.
optimize!(model)