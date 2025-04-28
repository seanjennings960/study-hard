using Revise
includet("data.jl")
using .Data
using JuMP
import HiGHS
using DataFrames
using SparseArrays



# ############################################################################
# %% Load data
# ############################################################################

enet_file = joinpath(data_dir, "enet39.xlsx")
scenario_file = joinpath(data_dir, "scenario_events.xlsx")
profile_file = joinpath(data_dir, "full_year_profs.prfl")
network = Data.load_network_scenario(enet_file, profile_file, scenario_file)
println("Number of externals: $(length(network.externals))")
println("Number of nodes: $(length(network.nodes))")
println("Number of lines: $(length(network.lines))")


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

# %% Matrices and whatnot
A = incidence_matrix(network)
F = power_transfer_distribution_matrix(network)
@assert isapprox(F * [1; 0; -1], [1/3; 2/3; 1/3])
Ψ = bus_injection_matrix(network)

C, Φ_1, Φ_2, Φ_4 = configurable_power_limits(network)

Φ_4["Store"]

# %% Sets and some housekeeping...


T = 24
N = [n.name for n in network.nodes]
X = [x.name for x in network.externals]

n_N = length(N)

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

@variable(model, e[B, 1:T] >= 0)
@variable(model, e_max[C_E] >= 0)

# Configuration matrix
Φ_3 = spzeros(length(B), length(C_E))
for (j, configurable) in enumerate(C_E)
    i = findfirst(n -> n == configurable, B)
    Φ_3[i, j] = 1
end
E_fixed = [
    is_configurable(b) ? 0. : b.E_max
    for b in batteries
]

D = spzeros(T-1, T)
for t in 1:T-1
    D[t, t] = -1
    D[t, t+1] = 1
end

η_c = 0.96
η_d = 0.96


@variable(model, p_charge[B, 1:T])
@variable(model, p_discharge[B, 1:T] >= 0)
@constraint(model, c1[b in B],
    e[b, 1:T] .<= E_fixed .+ Φ_3 * [e_max[c] for c in C_E])
@constraint(model, [b=B],
    D * [e[b, t] for t in 1:T]  .== 
        η_c * p_charge[b, 1:end-1] .- 1/η_d * p_discharge[b, 1:end-1]
)
@constraint(model, [b=B], u[b, 1:T] .== p_discharge[b, 1:T] .- p_charge[b, 1:T])

p
p_upper
p_upper_b = hcat([transpose(p_upper[b]) for b in B]...)
keys(p_upper_b)
Φ_4["Store"]
@constraint(model, [b=B], p_charge[b, :] .<= p_upper[b] + Φ_4[b] * [p_max[c] for c in C])



# %% The cost of getting shit done.

C0 = Dict(
    "Fuel" => 20_000,
    "Ren" => 00_000,
    "Store" => 1_000
)
C1 = Dict(
    "Fuel" => 5,
    "Ren" => 0,
    "Store" => 0
)
C0_E = Dict(
    "Store" => 1_000
)
@objective(model, Min,
    sum(C0[c] * p_max[c] for c in C) + sum(C1[c] * sum(u[c, t] for t=1:T) for c in C)
    + sum(C0_E[b] * e_max[b] for b in B)
)

optimize!(model)

println("Objective value: $(objective_value(model))")
println("Storage Details: $(value.(p_max))")
value.(p_max)
value.(e_max)