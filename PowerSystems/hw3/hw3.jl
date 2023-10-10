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
    PS.print_values((; V2, I2, Z2, Z2_prime, Z2_prime_check))
end

problem_3_2()