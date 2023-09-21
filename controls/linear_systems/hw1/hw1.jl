using LinearAlgebra
A = [
    -1 1 0 0
    0.5 -1 0.5 0
    0 0.5 -1 0.5
    0 0 1 -1
]

p1 = [
     1   0  0 0 
    -1   1  0 0
     0  -1  1 0
     0   0 -1 1
]

p2 = [
    1 1 1 1
    0 1 1 1 
    0 0 1 1
    0 0 0 1
]

function change_basis(A, p_b2_b1)
    p_b1_b2 = p_b2_b1^-1
    println("Transform from B2 -> B1")
    display(A * p_b2_b1)
    println("Transform from B2 -> B2")
    display(p_b1_b2 * A * p_b2_b1)

end

function x_at_1(eAt, integral_part)
    x0 = [1; 0]
    B = [1; 0]
    return eAt * (x0 + integral_part * B)
end

function harmonic()
    eAt = [
        cos(1) sin(1)
        -sin(1) cos(1)
    ]
    println("part a")
    A = [0 1; -1 0]
    conv_a = A^-1 * (I - eAt^-1)
    println("by hand")
    display(
        [cos(1) + sin(1)
         cos(1) - sin(1) - 1]
    )
    println("computer")
    display(x_at_1(eAt, conv_a))
    # println("conv_a")
    # display(conv_a)

    println("part b")
    
    conv_b = A^-1 * (I + A^-1) * (I - eAt^-1)
    a = [cos(1); -sin(1)]
    b = [sin(1) - (cos(1) - 1); (cos(1) - 1) + sin(1)]
    println("by hand")
    display(
        a + b
    )
    println("computer")
    display(x_at_1(eAt, conv_b))

    println("part c")
    conv_c = 1/4 * [
        1 - cos(2) sin(2) - 2
        2 - sin(2) 1 - cos(2)
    ]
    display(x_at_1(eAt, conv_c))
end


# println("A")
# display(A)
# change_basis(A, p1)
# change_basis(A, p2)
harmonic()