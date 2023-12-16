# Load the packages
using PowerSystems
using PowerNetworkMatrices
using PowerFlows
using PowerSystemCaseBuilder
using LinearAlgebra
using SparseArrays

# Loads the System Data
sys = build_system(PSITestSystems, "c_sys14"; add_forecasts = false)

# Get a Reference Ybus positive sequence
ybus_ref = Ybus(sys)
# Reference power flow solution
res_f = solve_powerflow(ACPowerFlow(check_reactive_power_limits = false), sys; method = :newton)

# Type and build Ybus for short circuit calculations

zero_seq_lines = [
    # (from, to, R0, X0, B0)
    (2, 5, 0.17085, 0.52164, 0.102),
    (6, 12, 0.36873, 0.76743, 0),
    (12, 13, 0.66276, 0.59964, 0),
    (6, 13, 0.19845, 0.39081, 0),
    (6, 11, 0.28494, 0.5967, 0),
    (11, 10, 0.24615, 0.57621, 0),
    (9, 10, 0.09543, 0.2535, 0),
    (9, 14, 0.38133, 0.81114, 0),
    (14, 13, 0.51279, 1.04406, 0),
    (7, 9, 0, 0.33003, 0),
    (1, 2, 0.05814, 0.17751, 0.1584),
    (3, 2, 0.14097, 0.59391, 0.1314),
    (3, 4, 0.20103, 0.51309, 0.1038),
    (1, 5, 0.16209, 0.66912, 0.1476),
    (5, 4, 0.04005, 0.12633, 0.0384),
    (2, 4, 0.17433, 0.52896, 0.1122)
]

Ybus_zero_sequence = zeros(ComplexF64, 14, 14)
# Construct zero-sequence.
for (from, to, R0, X0, B0) in zero_seq_lines
    # for each transmission line
    Y0 = 1 / (R0 + im * X0)
    Ybus_zero_sequence[from, to] = -Y0
    Ybus_zero_sequence[to, from] = -Y0
    Ybus_zero_sequence[from, from] += Y0 + B0 / 2
    Ybus_zero_sequence[to, to] += Y0 + B0 / 2
end

# We add the self-admittance to the Yg side of Yg-Delta transformer-connected
# buses. For completeness, since there's no zero-sequence connections
# between 69kV and 13.9kV circuits.
y_delta_transformers = [
    # (from, x, alpha)
    (5, 0.25202, 0.932),
    (4, 0.55618, 0.969),
    (4, 0.20912, 0.978),
]
for (bus, X0, alpha) in y_delta_transformers
    Ybus_zero_sequence[bus, bus] += alpha^2 / (im * X0)
end



# We now take into account the loads on each bus by adding to the Ybus_ref, which
# only contains data from transmission lines and transformers.
Ybus_positive_sequence = Matrix(ybus_ref.data)
load_buses = sort!([load.bus.number for load in get_components(PowerLoad, sys)])


# We first compute the admittance for each load:
# We assume a constant impedance loads and compute the admittance
# from the powerflow by the formula Y_load = conj(S) / |V|^2
# where S is the complex power of the load, and |V| is the
# voltage magnitude
br = res_f["bus_results"]
V_pf = res_f["bus_results"][!, "Vm"]
S_load = br[load_buses, "P_load"] + im * br[load_buses, "Q_load"]
S_load /= 100  # Convert to per-unit
Y_load = conj!(S_load) ./ V_pf[load_buses].^2
for (bus, Y) in zip(load_buses, Y_load)
    # Each load is Y-grounded and so contributes to the self-admittance.
    # We assume that the load is well-grounded, so that Z_g, the ground impedance,
    # is zero. Thus, the zero-sequence admittance of the load is equal to positivie
    # and negative sequence admittances.
    Ybus_positive_sequence[bus, bus] += Y
    Ybus_zero_sequence[bus, bus] += Y
end
# We notice upon inspection of Y_load that for some reason, Q_load at bus 4
# is -3.9 MVar???? Even though in spreadsheet it is 0.
# println(get_component(PowerLoad, sys, "Bus4").reactive_power)


X_gen = Dict(
    1=>0.33,
    2=>0.23,
    3=>0.23,
    6=>0.22,
    8=>0.21
)

for (bus, x_gen) in pairs(X_gen)
    # The generators also each contribute self-admittance in positive and negative
    # sequence. Assume Y1 ~= Y2 (positive and negative sequence admittances are about
    # equal).
    y_gen = 1 / (im * x_gen)
    Ybus_positive_sequence[bus, bus] += y_gen
end
# All the generators except the one at bus8 are delta-delta transformers
# which don't pass zero-sequence current (and thus have zero admittance).
# At bus8 however, the transformer of the generator is "Y-grounded" (which we assume
# to mean Yg-Yg), which means that zero-sequence passes through. We assume that X0
# includes both transformer and generator zero sequence impedances.
Ybus_zero_sequence[8, 8] += 1 / (im * 0.06)

# We assume all components in the power system have equivalent zero and negative sequence
# impedances.
Ybus_negative_sequence = copy(Ybus_positive_sequence)


println("Positive sequence Admittance matrix [to column 10]")
display(round.(sparse(Ybus_positive_sequence[:, 1:9]), digits=3))
println("Positive sequence Admittance matrix [column 10 to end]")
display(round.(sparse(Ybus_positive_sequence[:, 10:end]), digits=3))
println("Zero sequence Admittance matrix [to column 10]")
display(round.(sparse(Ybus_zero_sequence[:, 1:9]), digits=3))
println("Zero sequence Admittance matrix [column 10 to end]")
display(round.(sparse(Ybus_zero_sequence[:, 10:end]), digits=3))



# Short Circuit calculations.
# Employ the equations from the class lectured to obtain the short circtuit values.
# Focus on Lecture 19

# Bus Fault location
bus_number = 14

a = 1*exp(1im*(2*π/3))
A012 = [1 1 1
        1 a^2 a
        1 a a^2 ]

# Invert admittance matrix to get impedance matrix for each sequence.
Z_0 = pinv(Ybus_zero_sequence)
Z_1 = pinv(Ybus_positive_sequence)
Z_2 = pinv(Ybus_negative_sequence)
# Z[k,k] is the thevenin equivalent impedance at bus k. The impedance matrix
# takes Z[k,k] as its diagnoal elemnents for each sequence network.
Z_at_bus = Diagonal([Z[bus_number, bus_number] for Z in [Z_0, Z_1, Z_2]])

# Positive sequence voltage comes from power flow result. Zero and negative
# sequence are 0.
V_012 = [0, V_pf[bus_number], 0]

I_rated = 100 / 69 * 1000  # A
V_rated = [get_component(ACBus, sys, "Bus $i").base_voltage for i in range(1, 14)]

# Z_f for a 3-phase fault is zeros(3, 3)
I_fault_3_phase = pinv(Z_at_bus) * V_012
I_abc_3_phase = abs.(A012 * I_fault_3_phase)
println("3-phase fault current (A): $(I_abc_3_phase * I_rated)")

# Compute fault current for line fault.
Y_fault_line = zeros(3, 3)
Y_fault_line[1, 1] = 1e6
Y_fault_012 = inv(A012)*Y_fault_line*A012
I_012 = pinv(Y_fault_012*Z_at_bus+ I(3))*Y_fault_012*V_012
I_abc = A012*I_012
I_abc_mag = abs.(I_abc)
println("line-to-ground (A): $(I_abc_mag * I_rated)")

e14 = zeros(14)
e14[bus_number] = 1

V_post_fault_012 = Dict()
for (name, I_fault) in zip(["3-phase", "line-to-ground"], [I_fault_3_phase, I_012])
    # N x 3 matrix of initial voltages, where N is number of buses.
    V_012 = [zeros(14) V_pf zeros(14)]
    # N x 3 matrix of change in injected currents at each node.
    # Only fault bus has change in voltage
    delta_I = e14 * transpose(I_fault)
    delta_V = hcat(
        [Z * delta_I[:, i] for (i, Z) in enumerate([Z_0, Z_1, Z_2])]...
    ) 

    V_post_fault_012[name] = V_012 - delta_V
    # Each row of V_k be the k-th row of V_post_fault (shape Nx3)
    # (the 012 sequence voltage at bus k), then V_k_abc = A * V_k.
    # Taking the transpose yields: V_k_abc^T = V_k^T A^T
    # A vertical stack across the rows of V_post_fault results with:
    V_abc = V_post_fault_012[name] * transpose(A012)
    println("Phase voltages for each bus with $name fault (kV):")
    display(V_rated .* abs.(V_abc))
end


# # Part c.
# #### Write the code below to calculate the currents through the lines

for (from, to) in [(9, 14), (13, 14)]
    Y_line = -[Ybus[from, to] for Ybus in [
        Ybus_zero_sequence,
        Ybus_positive_sequence,
        Ybus_negative_sequence
    ]]
    for (name, V_fault) in pairs(V_post_fault_012)
        I_fault_line = Y_line .* (V_fault[from, :] - V_fault[to, :])
        I_fault_phase = A012 * I_fault_line
        println("Phase current (A) in line ($from, $to) for $name fault")
        display(abs.(I_fault_phase) * I_rated)
    end
end
