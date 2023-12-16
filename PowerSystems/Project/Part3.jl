# Load the packages
using PowerSystems
using PowerNetworkMatrices
using PowerFlows
using PowerSystemCaseBuilder
using PlotlyJS

# Loads the System Data
sys = build_system(PSITestSystems, "c_sys14"; add_forecasts = false)

# Get the load under study
load = get_component(PowerLoad, sys, "Bus14")

# Get the base power flow case
p_base = get_active_power(load)
q_base = get_reactive_power(load)



######################### CPF Loop ##########################
function run_cpf()
    step_size = 0.1
    change_factor = 0.01
    λ_init = 0.0
    λ_results = Float64[]
    V_results = Float64[]
    while step_size > 1e-5
        println("STEPSIZE: $step_size")
        for λ in range(λ_init, step = step_size, length = 1_000_000)
            set_active_power!(load, p_base*λ)
            set_reactive_power!(load, q_base*λ)
            res = try
                solve_powerflow(ACPowerFlow(check_reactive_power_limits = true), sys; method = :newton)
            catch e
                println("Error (breaking loop): $e")
                false
            end
            if res == false
                break
            else
                push!(λ_results, λ)
                push!(V_results, res["bus_results"][14, "Vm"])
            end
        end
        step_size = step_size*change_factor
        λ_init = last(λ_results)
    end
    return (λ_results, V_results)
end

function cpf_scatter(name)
    x, y = run_cpf()
    return scatter(x=x, y=y, name=name)
end

traces = AbstractTrace[]
push!(traces, cpf_scatter("Line4 Online | No Capacitor"))

# Get the line for the trip
line = get_component(Line, sys, "Line4")
set_available!(line, false)

push!(traces, cpf_scatter("Line4 Offline | No Capacitor"))



# Choose a bus to add the capacitor
bus_14 = get_component(ACBus, sys, "Bus 14")

# Create the capacitor. Y is a complex number so Y = 1m* capacitor_size_in_pu
capacitor_size_in_pu = 0.235
capacitor = FixedAdmittance(
                name = "Capacitor",
                available = true,
                bus = bus_14, # Place here the chosen Bus
                Y = 1im*capacitor_size_in_pu
)

capacitor_label = "$capacitor_size_in_pu p.u. Capacitor, Bus 14"
add_component!(sys, capacitor)
set_available!(line, true)
push!(traces, cpf_scatter("Line4 Online | $capacitor_label"))
set_available!(line, false)
push!(traces, cpf_scatter("Line4 Offline | $capacitor_label"))


layout = Layout(title="PV Curve under Various Conditions",
                xaxis=attr(title="Load (MW)"),
                yaxis=attr(title="Voltage (p.u.)"),
                yaxis_range=[0, 1.2], xaxis_range=[0, 6])
plot(traces, layout)
# plot([trace1, trace2, trace4])
