# includet("network.jl")
# using .NetworkMod
using JuMP
import HiGHS
# using DataFrames
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

function emissions_by_tech(tech)
    if tech == "coal"
        return 0.916
    elseif tech == "gas_cc"
        return 0.43
    else
        return 0
    end
end

function emissions_factor(network)
    return [
        isa(e.type, Demand) ? 0 : emissions_by_tech(e.type.tech)
        for e in network.externals
    ]
    return emissions_factor
end


function emissions(network, model)
    ϵ_E = emissions_factor(network)
    X = [e.name for e in network.externals]
    T = n_timesteps(network)
    e1 = sum(sum(ϵ * model[:u][x, t] for (x, ϵ) in zip(X, ϵ_E)) for t in 1:T)
    
    # e2 = sum(e1 for t in 1:T)
    return e1

end


function capacity_expansion(network::Network, cost::LinearCost, ϵ_max::Union{Nothing, Float64}=nothing)

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
    ϵ = emissions(network, model)
    if !isnothing(ϵ_max)
        @constraint(model, c_emissions, ϵ <= ϵ_max)
    end



    ########################
    # Objective
    ########################

    C0 = cost.C0
    C1 = cost.C1
    C0_E = cost.C0_E
    total_power_capital = sum(C0[c] * p_max[c] for c in C) * 1000 # $ / kW /year * MW * (1000kW/MW) == $
    total_power_operational = sum(C1[c] * sum(u[c, t] for t=1:T) for c in C) * 8760 / T # $/MWh/(T hr) * MWh * (8760 hr / year)== $ FIXME: Assuming 1 hr Δ_t
    # HACK: multiple by some factor to scale operational vs capital costs -- gives a lever in comparing
    # short-term vs. long term costs
    # total_power_operational_pre = sum(C1[c] * sum(u[c, t] for t=1:T) for c in C) * 8760 / T # $/MWh/(T hr) * MWh * (8760 hr / year)== $ FIXME: Assuming 1 hr Δ_t
    # total_power_operational = 100 * total_power_operational_pre
    total_energy_capital = sum(C0_E[b] * e_max[b] for b in B) * 1000 # $ / kWh/year * MWh * (1000kWh / MWh) == $/year
    @objective(model, Min,
        total_power_capital + total_power_operational
        + total_energy_capital
    )
    return model
end


# ############################################################################
# %% Model Analytics
# ############################################################################

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
