using Plots

# Move these to library??
phasor(A, ϕ) = A * exp((ϕ)im)
phasordeg(A, θ) = phasor(A, deg2rad(θ))
phasor_from_p2p(A, θ) = phasor(A / √(2), θ)
phasor_from_p2p_deg(A, θ) = phasordeg(A / √(3), θ)


function print_phasor(a, deg=true)
    a_ang = angle(a)
    if deg
        a_ang = rad2deg(a_ang)
    end
    println("Phasor: $(abs(a)) ∠ $(a_ang)°")
    println("Complex: $a")
end

function pf_from_complex(S)
    return cos(angle(S))
end

function parallel(Z1, Z2)
    return (1/Z1 + 1/Z2)^-1
end

function series(Z1, Z2)
    return Z1 + Z2
end

function leading_lagging(S)
    a = angle(S)
    if sign(a) == -1
        # Since β is subtracted from δ to obtain the
        # complex power. +β means leading current
        # but negative reactive power (as in this conditional).
        # It is still called leading.
        return "leading"
    elseif sign(a) == 1
        return "lagging"
    else
        return "purely resistive"
    end
end


function problem_2_10()
    V = phasor_from_p2p_deg(678.8, -15 - 90)
    I = phasor_from_p2p_deg(200, -5)
    δ = angle(V)
    β = angle(I)
    pf = cos(δ - β)
    println("PF: $pf")
    s = V * conj(I)
    println("PF (from power angle): $(cos(angle(s)))")
    println("V:")
    print_phasor(V)
    println("I:")
    print_phasor(I)
    println("S:")
    print_phasor(s)
end

function problem_2_11()
    V = 277
    ω = 2 * π * 60
    Z_R = 20
    Z_L = im * (ω * .01)
    Z_C = - im * 25
    for (Z, name) in zip([Z_R, Z_L, Z_C], ["Z_R", "Z_L", "Z_C"])
        println(name)
        S = V^2 / conj(Z)
        print_phasor(S)
        println("Sign: $(sign(angle(S)))")
        println("pf: $(pf_from_complex(S))")
        println(leading_lagging(S))
    end
end

function problem_2_12()
    V = phasor_from_p2p_deg(678.8, 45)
    println("V")
    print_phasor(V)
    Z_R = 10
    Z_C = -im * (25)
    Z = parallel(Z_R, Z_C)
    println("Z")
    print_phasor(Z)
    S = abs(V)^2 / conj(Z)
    S_R = conj(Z_C / (Z_R + Z_C)) * S
    S_C = conj(Z / Z_C) * S
    pf = pf_from_complex(S)
    leading = leading_lagging(S)
    println("S")
    print_phasor(S)
    println("S_R")
    print_phasor(S_R)
    println("S_C")
    print_phasor(S_C)
    println("pf: $pf")
    println(leading)
    S_R = abs(V)^2 / conj(Z_R)
    S_C = abs(V)^2 / conj(Z_C)
    println("S_R")
    print_phasor(S_R)
    println("S_C")
    print_phasor(S_C)
end

function problem_2_13()
    V = phasor_from_p2p_deg(678.8, 45)
    Z_R = 10
    Z_C = -im * (25)
    Z = series(Z_R, Z_C)
    I = V / Z
    println("I")
    print_phasor(I)
    S = Z * abs(I)^2
    S_R = Z_R * abs(I)^2
    S_C = Z_C * abs(I)^2
    pf = pf_from_complex(S)
    leading = leading_lagging(S)
    println("S")
    print_phasor(S)
    println("S_R")
    print_phasor(S_R)
    println("S_C")
    print_phasor(S_C)
    println("pf: $pf")
    println(leading)
end

function print_phasors(values)
    for (name, v) in pairs(values)
        println(name)
        print_phasor(v)
    end
end

function instantaneous(V, ω, t)
    return √2 * abs(V) * cos.(ω * t .+ angle(V))
end

function instantaneous_power(S, ω, t, δ)
    angles = 2 * (ω * t .+ δ)
    return (
        real(S) * (1 .+ cos.(angles))
        + imag(S) * sin.(angles)
    )
end

function problem_2_15()
    V = phasor_from_p2p_deg(4, 60)
    Z = phasordeg(2, 30)
    I = V/Z
    S = V * conj(I)
    print_phasors((; Z, V, I, S))

    omega = 2 * π * 60
    t = range(0, 0.1, 1000)
    v = instantaneous(V, omega, t)
    i = instantaneous(I, omega, t)
    p = instantaneous_power(S, omega, t, angle(V))
    plot!(t, v, label="v(t)")
    plot!(t, i, label="i(t)")
    plot!(t, p, label="p(t)",
        title="Instantaneous Voltage, Current and Power",
        xlabel="Time (s)",
        ylabel="Voltage (V) | Current (A) | Power (W)"
    )
    savefig("Images/instantaneous.png")
    gui()
end

function problem_2_16()
    V = phasordeg(120, 0)
    omega = 2 * π * 60
    Z_R = 10
    L = 40e-3
    Z_L = im * omega * L
    Z = Z_R + Z_L
    S = abs(V)^2 / conj(Z)
    W = L * (abs(V / Z))^2
    println("PF: $(pf_from_complex(S))")
    println(leading_lagging(S))
    print_phasors((; S, Z))
    println("W: $W")
    println("ωW: $(omega * W)")
end

function problem_2_20()
    Z1 = phasordeg(20, 30)
    Z2 = phasordeg(14.14, -45)
    V = phasordeg(100, 60)
    Z = (1/Z1 + 1/Z2)^-1
    S1 = abs(V)^2 / conj(Z1)
    S2 = abs(V)^2 / conj(Z2)
    S = abs(V)^2 / conj(Z)
    print_phasors((; Z, S1, S2, S))
end

function problem_2_21()
    pf = 0.7
    pf_t = 0.9
    P = 1000
    diffQ = P * (tan(acos(pf_t)) - tan(acos(pf)))
    println("Delta Q: $diffQ")
    Q = P * tan(acos(pf))

    P_new = 1000 * 0.746 / 0.9
    pf_new = cos(atan(P_new / Q))
    println("pf_new: $pf_new")
end

function problem_2_22()
    P = 2000 
    Z1 = 3 + im * 5
    Z2 = 10
    Z = (1/Z1 + 1/Z2)^-1
    Q = P * tan(angle(Z))
    S = P + im * Q
    S1 = conj(Z / Z1) * S
    S2 = conj(Z / Z2) * S
    I = √(S / Z)
    print_phasors((; Z, S, S1, S2, I))
end

function problem_2_23()
    V = 120
    I = phasordeg(25, 30)
    S = V * conj(I)
    print_phasors((; S))
end

function S_from_P_pf(P, pf, leading)
    dir = if leading; -1 else 1 end
    Q = P * tan(dir * acos(pf))
    return P + im * Q
end

function problem_2_24()
    S1 = 10
    S2 = phasor(10, acos(0.9))
    P3 = 10 * 0.746 / 0.85 
    S3 = S_from_P_pf(P3, 0.95, true)
    S = S1 + S2 + S3
    print_phasors((; S1, S2, S3, S))
end

function problem_2_25()
    Z_R = 3
    Z_L = im * 8
    Z_C = - im * 4
    Z = Z_R + Z_L + Z_C
    V = 100
    I = V / Z
    S_R = Z_R * abs(I)^2
    S_L = Z_L * abs(I)^2
    S_C = Z_C * abs(I)^2
    S_sum = S_R + S_L + S_C
    S_total = abs(V)^2 / conj(Z)
    print_phasors((; I, S_R, S_L, S_C, S_sum, S_total))
end

function problem_2_26()
    Z_L = im
    P_p = 120000
    pf = 0.85
    V_p = 480
    S_p = S_from_P_pf(P_p, pf, false)
    I = conj(S_p / V_p)
    S_L = Z_L * abs(I)^2
    S = S_p + S_L
    V = S / conj(I)
    pf = pf_from_complex(S)


    Z_p = conj(abs(V_p)^2 / S_p)
    Z = Z_p + Z_L
    V_total = Z / Z_p * V_p
    I2 = V_p / Z_p
    S_circuit = V_total * conj(I2)
    pf_circuit = pf_from_complex(S_circuit)

    print_phasors(
        (; S_p, I, S_L, S, V, pf, Z_p,
        Z, V_total, I2, S_circuit, pf_circuit))
end

function problem_2_27()
    pf = 0.8
    pf_t = 0.95
    P = 50000
    dQ = P * (tan(acos(pf_t)) - tan(acos(pf)))
    V = 220
    omega = 2 * π * 60
    C = -dQ / omega / V^2
    # Sanity check
    Z_C = -im / (omega * C)
    S = V^2 / conj(Z_C)
    print_phasors((; dQ, C, Z_C, S))
end

function problem_2_28()
    V = 240
    S1 = 12 + im * 6.667
    S2 = phasor(4, -acos(0.96))
    S3 = 15
    S = S1 + S2 + S3
    Z = V^2 / conj(S)
    # R_s = real(Z)
    # X_s = imag(Z)
    R_p = Z * conj(Z) / real(Z)
    X_p = Z * conj(Z) / imag(Z)
    Z_parallel = (1 / R_p + 1 / (im * X_p))^-1
    print_phasors((; S1, S2, S3, S, Z, R_p, X_p, Z_parallel))
end


# problem_2_10()
# problem_2_11()
# problem_2_12()
# problem_2_13()
# problem_2_15()
# problem_2_16()
# problem_2_20()
# problem_2_21()
# problem_2_22()
# problem_2_23()
# problem_2_24()
# problem_2_25()
# problem_2_26()
# problem_2_27()
problem_2_28()