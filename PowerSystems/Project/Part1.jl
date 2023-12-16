# Load the packages
using PowerSystems
using PowerFlows
using PowerSystemCaseBuilder



# Loads the System Data
sys = build_system(PSITestSystems, "c_sys14"; add_forecasts = false)
##### Parts a, b
# Solution to the PowerFlow. Change the check_reactive_power_limits flag to obtain results
# For each case.
res_without_limits = solve_powerflow(
    ACPowerFlow(check_reactive_power_limits = false), sys; method = :newton)
res_with_limits = solve_powerflow(
    ACPowerFlow(check_reactive_power_limits = true), sys; method = :newton)
println("With limits")
display(res_with_limits["bus_results"])
display(res_with_limits["flow_results"])
println("With limits")
display(res_without_limits["bus_results"])
display(res_without_limits["flow_results"])
diff = (res_with_limits["bus_results"][!, "Q_gen"] -
    res_without_limits["bus_results"][!, "Q_gen"])
println("diff in Q_gen")
display(diff)

##### Part d. Increase the loading loop
λ = 1.4
for g in get_components(PowerLoad, sys)
    set_active_power!(g, get_active_power(g)*λ)
    set_reactive_power!(g, get_reactive_power(g)*λ)
end

# Solve again
with_limits = solve_powerflow(ACPowerFlow(check_reactive_power_limits = true), sys; method = :newton)
without_limits = solve_powerflow(ACPowerFlow(check_reactive_power_limits = false), sys; method = :newton)
println("Increased loading 40% || With limits")
display(with_limits["bus_results"])
display(without_limits["flow_results"])
diff = (with_limits["bus_results"][!, "Q_gen"] -
    without_limits["bus_results"][!, "Q_gen"])
println("Increased loading 40% ||  without limits")
display(without_limits["bus_results"])
display(without_limits["flow_results"])
println("diff in Q_gen")
display(diff)

##### Parts d and e

capacitor_size_in_pu_13 = 0.176
capacitor_size_in_pu_14 = 0.235

# Choose a bus to add the capacitor
bus_13 = get_component(ACBus, sys, "Bus 13")
bus_14 = get_component(ACBus, sys, "Bus 14")

# Create the capacitor. Y is a complex number so Y = 1m* capacitor_size_in_pu
capacitor = FixedAdmittance(
                name = "Capacitor",
                available = true,
                bus = bus_13, # Place here the chosen Bus
                Y = 1im*capacitor_size_in_pu_13
)
existing_cap = get_component(FixedAdmittance, sys, "Capacitor")
if !isnothing(existing_cap)
    remove_component!(sys, existing_cap)
end
add_component!(sys, capacitor)
# else
#     capacitor.Y = im * capacitor_size_in_pu_13
# end

# Solve again and compare the results
with_cap_13 = solve_powerflow(ACPowerFlow(check_reactive_power_limits = true), sys; method = :newton)



remove_component!(sys, capacitor)
# Create the capacitor. Y is a complex number so Y = 1m* capacitor_size_in_pu
capacitor = FixedAdmittance(
                name = "Capacitor",
                available = true,
                bus = bus_14, # Place here the chosen Bus
                Y = 1im*capacitor_size_in_pu_14
)
add_component!(sys, capacitor)

with_cap_14 = solve_powerflow(ACPowerFlow(check_reactive_power_limits = true), sys; method = :newton)
println("Without cap:")
display(with_limits["bus_results"])
println("With cap 13:")
display(with_cap_13["bus_results"])
println("With cap 14:")
display(with_cap_14["bus_results"])
println("Flow results")
println("With cap 13:")
display(with_cap_13["flow_results"])
println("With cap 14:")
display(with_cap_14["flow_results"])