import PowerSystems as PS

function problem_3_2()
    N1 = 2000
    N2 = 500
    V1 = PS.phasordeg(1000, 0)
    I1 = PS.phasordeg(5, -30)
    alpha = N1/N2
    V2 = V1 / alpha
    I2 = I1 * alpha
    Z2 = V2/I2
    Z2_prime = alpha^2 * Z2
    Z2_prime_check = V1 / I1
    PS.print_values((; alpha, V2, I2, Z2, Z2_prime, Z2_prime_check))
end

function problem_3_4()
    alpha = 2400 / 240
    V2 = 230
    S2_mag = 80000
    pf = 0.8

    S2 = S2_mag * (pf + im * sin(acos(pf)))
    V1 = alpha * V2
    Z2 = abs(V2)^2 / conj(S2)
    Z2_prime = alpha^2 * Z2
    PS.print_values((; S2, V1, Z2, Z2_prime))
end

function problem_3_8()
    V_in = 18/√(2)
    V_r1 = 18
    S_rated = 18^2
    alpha = 2
    R = [18, 36, 2, 8]

    # Find rated impedances
    Z_r1 = S_rated / V_r1^2
    Z_r2 = Z_r1 / alpha^2

    # Convert to per-unit voltage + resistance
    V_in_pu = V_in / V_r1
    Z_r = [Z_r1, Z_r1, Z_r2, Z_r1]
    R_pu = R ./ Z_r

    # Solve circuit.
    R_p_pu = (1 / R_pu[2] + 1 / (R_pu[3] + R_pu[4]))^-1
    V_2_pu = R_p_pu / (R_pu[1] + R_p_pu) * V_in_pu
    V_out_pu = R_pu[4] / (R_pu[3] + R_pu[4]) * V_2_pu
    V_out_rms = V_out_pu * V_r1
    V_out = V_out_rms * √(2)


    PS.print_values((; Z_r1, Z_r2, V_in_pu, R_pu, R_p_pu, V_2_pu, V_out_pu,
                     V_out_rms, V_out))

end

function problem_3_14()
    # Inputs
    V_r1 = 2400
    V_r2 = 240
    Sr = 50000
    Z1 = 1 + 2 * im
    Z2 = 1 + 2.5 * im
    pf = 0.8
    V3 = V_r2

    alpha = V_r1 / V_r2
    S3_pu = pf + im * sin(acos(pf))

    # Without per-unitization
    S3 = Sr * S3_pu 
    I1 = conj(S3) / V_r1
    V2 = V_r1 + Z2 * I1
    V1 = V2 + Z1 * I1
    S = S3 + (Z1 + Z2) * abs(I1)^2

    # With per-unitization
    Z_r1 = (V_r1)^2 / Sr
    Z_1_pu = Z1 / Z_r1
    Z_2_pu = Z2 / Z_r1
    I_pu = conj(S3_pu)

    V_2_pu = 1 + Z_2_pu * I_pu
    V_1_pu = 1 + (Z_1_pu + Z_2_pu) * I_pu
    S_pu = (Z_1_pu + Z_2_pu) + S3_pu

    # Check:
    V2_check = V_2_pu * V_r1
    V1_check = V_1_pu * V_r1
    S_check = S_pu * Sr

    PS.print_values((; alpha, S3_pu, S3, Z1, Z2, I1, V2, V1, S, Z_r1, Z_1_pu, Z_2_pu, I_pu,
                  V_2_pu, V_1_pu, S_pu, V2_check, V1_check, S_check))

end

function problem_3_23()
    S_r = 100e6
    Z_l1 = 48.4
    Z_l2 = 65.43
    S_L_mag = 57e6
    pf = 0.6
    V_L = 10.45e3

    # Rated voltages, deduced from nominal
    V_r_l1 = 220e3
    V_r_l2 = 110e3
    V_r_4 = 11e3

    # Line impedances
    Z_l1_pu = Z_l1 * S_r / V_r_l1^2
    Z_l2_pu = Z_l2 * S_r / V_r_l2^2

    # Load impedance
    S_L = S_L_mag * (pf + im * sin(acos(pf)))
    Z_L_pu = V_L^2 / V_r_4^2 * (S_r / conj(S_L))

    PS.print_values((; Z_l1_pu, Z_l2_pu, S_L, Z_L_pu))
end

function problem_8_10()
    a = PS.phasordeg(1, 120)
    v_p_lg = [PS.phasordeg(280, 0), PS.phasordeg(250, -110), PS.phasordeg(290, 130)]
    # Move these to PowerSystems.jl??
    A = [
        1 1 1
        1 a^2 a
        1 a a^2
    ]
    B = [
        1 -1 0
        0 1 -1
        -1 0 1
    ]
    v_s_lg = A^-1 * v_p_lg
    v_p_ll = B * v_p_lg
    v_s_ll = A^-1 * v_p_ll
    PS.print_values((;v_s_lg, v_p_ll, v_s_ll))
end

function problem_8_13()
    a = PS.phasordeg(1, 120)
    I_delta = [PS.phasordeg(10, 0), PS.phasordeg(15, -90),
        PS.phasordeg(20, 90)]
    A = [
        1 1 1
        1 a^2 a
        1 a a^2
    ]
    B = [
        1 -1 0
        0 1 -1
        -1 0 1
    ]
    I_s_delta = A^-1 * I_delta
    I_L = transpose(B) * I_delta
    I_s_L = A^-1 * I_L

    PS.print_values((; I_s_delta, I_L, I_s_L))

end

function problem_3_27()
    S_rated = 500e6
    S_rated2 = 100e6
    V_r1 = 220e3
    V_r2 = 22e3
    V_r3 = 230e3
    Z = 0.1

    Z_r2 = V_r2^2 / S_rated
    Z_pu = Z / Z_r2

    Z_r1 = V_r1^2 / S_rated
    Z_1 = Z_pu * Z_r1
    Z_r3 = V_r3^2 / S_rated2
    Z_3pu = Z_pu * (V_r1 / V_r3)^2
    PS.print_values((; Z_r2, Z_pu, Z_3pu, Z_r1, Z_1, Z_r3))
end

function problem_8_14()
    Z_y = 12 + im * 16 
    Z_s_inv = [
        0 0 0
        0 1/Z_y 0
        0 0 1/Z_y
    ]
    V_ag = PS.phasordeg(280, 0)
    V_bg = PS.phasordeg(250, -110)
    V_cg = PS.phasordeg(290, 130)

    V_s = PS.A^-1 * [V_ag, V_bg, V_cg]
    I_s = Z_s_inv * V_s
    I = PS.A * I_s
    PS.print_values((;V_s, I_s, I))
end


problem_3_27()