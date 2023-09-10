using Plots


a = 1 + 2
# print(a)

phasor(A, ϕ) = A * exp((ϕ)im)
phasordeg(A, θ) = phasor(A, deg2rad(θ))

function print_phasor(a, deg=true)
    a_ang = angle(a)
    if deg
        a_ang = rad2deg(a_ang)
    end
    println("Phasor: $(abs(a)) ∠ $(a_ang)°")
    println("Complex: $a")
end

function problem2_2c()
    a = phasordeg(4/√(2), -30)
    b = phasordeg(5, -75)
    c = a + b
    println('a')
    print_phasor(a)
    println('b')
    print_phasor(b)
    println('c')
    print_phasor(c)
end

function optimal_capacitor(R, L)
    C = L / (R^2 + L^2)
    println("C: $C")
    println("1/C: $(1/C)")
    numerator = L - 1im * R
    denominator = R*C + 1im * (R*C - 1)
    println("RC - j(RC-1): $(denominator)")
    println("angle(L - jR): $(angle(numerator))")
    println("angle(RC - j(RC-1)): $(angle(denominator))")
    println("num/dem: $(numerator/denominator)")
    X_c = -(C^-1)im
end

function problem2_4()
    R = 8
    L = 6
    X_rl = R + (L)im
    X_c = -6im
    # X_c = optimal_capacitor(R, L)
    println("X_c: $X_c")
    println("X_c * X_rl: $(X_c * X_rl)")
    println("angle X_c * X_rl: $(angle(X_c * X_rl))")
    println("X_c + X_rl: $(X_c + X_rl)")
    println("angle X_c + X_rl: $(angle(X_c + X_rl))")
    X_total = X_rl * X_c / (X_rl + X_c)
    I = phasordeg(10, 0)
    V = X_total * I
    I1 = V / X_rl
    I2 = V / X_c
    println("X_total")
    print_phasor(X_total)
    println("I")
    print_phasor(I)
    println("V")
    print_phasor(V)
    println("I1")
    print_phasor(I1)
    println("I2")
    print_phasor(I2)

    lines = [I, I1, I2, V]
    labels = ["I", "I1", "I2", "V"]
    lim = 70
    for (line, label) in zip(lines, labels)
        plot!([0, real(line)], [0, imag(line)], label=label,
            markershape=:circle,
            xlims=(-lim, lim),
            ylims=(-lim, lim),
            title="Phasor plot",
            xlabel="Real (Voltage (V) and Current (A))",
            ylabel="Imag (Voltage (V) and Current (A))",
            show=true)
    end
    savefig("phasor_plot.png")
    gui()
    readline()
end

function problem2_5()
    V = phasordeg(277, 30)
    omega = 2 * π * 60  # rad/s
    L = 0.01  # H
    Z_R = 20  # ohm
    Z_L = 1im * (omega * L)
    Z_C = -25im
    println("omega: $omega")
    println("impedance inductor: $Z_L")
    println("I (resistor load)")
    print_phasor(V / Z_R)
    println("peak: $(√(2) * abs(V / Z_R))")
    println("I (inductor load)")
    print_phasor(V / Z_L)
    println("peak: $(√(2) * abs(V / Z_L))")
    println("I (capacitor load)")
    print_phasor(V / Z_C)
    println("peak: $(√(2) * abs(V / Z_C))")
end

function problem2_6()
    V = phasordeg(100/√(2), -30)
    print_phasor(V)
    println("100√2: $(100 * √2)")
end

function problem2_7()
    Z = 3 + 4im
    I = 100 / Z
    print_phasor(I)
    pf = cos(angle(I))
    println("angle: $(rad2deg(angle(I)))")
    println("PF: $pf")
end

function problem2_8()
    omega = 377
    L_T = 30.6e-6
    L_L = 5e-3
    C = 921e-6
    println("Z_L_T: $(1im * omega * L_T)")
    println("Z_L_L: $(1im * omega * L_L)")
    println("Z_C: $(1/(1im * omega * C))")
end

function problem2_9()
    V_total = 120
    Z_total = V_total / 60
    Z_load = Z_total - (0.1 + 0.5im)
    V_load = (Z_load/Z_total) * V_total
    println("V_load: $V_load")
    print_phasor(V_load)
end

function problemb()
    V = phasordeg(10/√2, 0)
    omega = 2 * π * 60
    Z_R1 = 10
    Z_R2 = 7
    C = 1e-6
    L = 50e-3
    Z_C = (1im * omega * C)^-1
    Z_L = 1im * omega * L

    println("Z_C: $Z_C")
    println("Z_L: $Z_L")
    # Intermediate terms
    Z_LC = (1/Z_C + 1/Z_L)^-1
    Z_RLC = (1/Z_L + 1/(Z_R2 + Z_C))^-1
    println("Z_LC: $Z_LC")
    println("Z_RLC: $Z_RLC")

    Z_circuits = [
        Z_R1 + Z_C,
        Z_L + Z_C + Z_R1,
        Z_R1 + Z_LC,
        Z_R1 + Z_RLC,
        Z_R1 + Z_L
    ]
    names = ["a", "b", "c", "d", "e"]

    for (z, name) in zip(Z_circuits, names)
        println("Z $name")
        print_phasor(z)
        println("I $name")
        print_phasor(V / z)
    end
end



# problem2_2c()
# problem2_4()
# problem2_5()
# problem2_6()
# problem2_7()
# problem2_8()
# problem2_9()
problemb()
