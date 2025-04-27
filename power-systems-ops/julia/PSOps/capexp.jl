
include("data.jl")
using .Data
using JuMP
import HiGHS
using DataFrames
using LinearAlgebra

# %%

using SparseArrays


# ############################################################################
# %% Load data
# ############################################################################

network = Data.load_network(joinpath(data_dir, "enet39.xlsx"))
println("Number of nodes: $(length(network.nodes))")
println("Number of lines: $(length(network.lines))")

#%% 


profiles = Data.load_profiles(
    joinpath(data_dir, "full_year_profs.prfl")
)

for profile in profiles
    println(profile.name)
    println(length(profile.data))
end


# ############################################################################
# %% Simple Test Case
# ############################################################################

nodes = [
    Node("1"), Node("2"), Node("3")
]
lines = [
    Line("L1", "2", "1", 1),
    Line("L2", "3", "1", 1),
    Line("L3", "3", "2", 1),
]
externals = [
    External("Fuel", "1", FuelGenerator()),
    External("Ren", "2", RenewableGenerator()),
]
network = Network(externals, nodes, lines)

profiles = Dict(
    "Fuel" => zeros(24),
    "Ren" => vcat(ones(12), zeros(12))
)

costs = Dict(
    "Fuel" => 5,
    "Ren" => 0,
)

# %%

struct ModelParams
    N::Vector{String}  # Set of Node Names
    E::Vector{String}  # Set of External Names
    L::Vector{String}  # Set of Line Names
    A::SparseMatrixCSC  # Incidence Matrix
    F::SparseMatrixCSC  # Power Transfer Distribution Matrix
end

function incidence_matrix(N::Vector{String}, lines::Vector{Line})
    n_N = length(N)
    n_L = length(lines)
    A = spzeros(n_L, n_N)
    for (i, l) in enumerate(lines)
        j = findfirst(n -> n == l.to, N)
        A[i, j] = -1
        k = findfirst(n -> n == l.from, N)
        A[i, k] = 1
    end
    return A

end


function extract_params(network::Network, profile::Dict{String, Profile})
    N = [n.name for n in nodes]

    # Incidence Matrix
    A = incidence_matrix(N, lines)
    B = Diagonal([l.B for l in lines])
    F = B * A * inv(Matrix(transpose(A) * B * A))

    return ModelParams(
        N,
        [e.name for e in externals],
        [l.name for l in lines],
        A, F
    )
end



p = extract_params(network, profiles)

# %%


model = Model(HiGHS.Optimizer)
@variable()