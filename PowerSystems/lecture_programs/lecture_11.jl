using LinearAlgebra

function phasor(A, δ)
    A * exp(δ * im)
end

function phasordeg(A, δ)
    phasor(A, deg2rad(δ))
end

function admittance_matrix_from_edges(N, Zs)
    Y = zeros(Complex{Float64}, N, N)
    edges = Dict((i, Array{Complex{Float64}}(undef, 0)) for i in 1:N)
    for (i, j, z) in Zs
        y_ij = 1/z
        push!(edges[i], y_ij)
        push!(edges[j], y_ij)
        Y[i, j] = - y_ij
        Y[j, i] = - y_ij
    end
    for i in 1:N
        Y[i,i] = sum(edges[i])
    end
    Y
end

function line_power_flow(Y, V)
    delta_V = V .- transpose(V)
    return delta_V .* conj.(- Y .* delta_V)
end

function print_matrices(values; args...)
    for (name, v) in pairs(values)
        println(name)
        display(round.(v; sigdigits=3, args...))
    end
end

function pf_3_node(V)
    Zs = [
        (1, 2, 0.03 + 0.3im),
        (2, 3, 0.06 + 0.2im)
    ]
    N = 3
    Y = admittance_matrix_from_edges(N, Zs)
    I = Y * V
    S = diagm(V) * conj(I)
    S_line = line_power_flow(Y, V)
    print_matrices((; Y, I, S, S_line))
    # Y_approx = [
    #     0.33 - 3.3003 * im      -0.33 + 3.3003 * im      0
    #     -0.33 + 3.3003 * im     1.7062 - 7.8875 * im     -1.3761 + 4.5872 * im
    #     0                       -1.3761 + 4.5872 * im    1.3761 - 4.5872 * im
    # ]
    # delta_I = (Y - Y_approx) * V
    # print_matrices((; Y, I, S, S_line, delta_I))
end

function example1()
    println("No phase diff")
    V = [1, 1, 1.1]
    pf_3_node(V)
    println("Voltage (node 3) leading")
    V = [1, 1, phasor(1.1, 0.1)]
    pf_3_node(V)
end

example1()