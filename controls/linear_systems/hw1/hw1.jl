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

function harmonic()
    println("part a")
    display(
        [cos(1) + sin(1)
         cos(1) + sin(1) - 1]
    )
end


# println("A")
# display(A)
# change_basis(A, p1)
# change_basis(A, p2)
harmonic()