module PowerSystems

######################################################################
###################     ANGLE REPRESENTATION     #####################
######################################################################

phasor(A, ϕ) = A * exp((ϕ)im)
phasordeg(A, θ) = phasor(A, deg2rad(θ))
# From peak2peak magnitude as argument returns a phasor with RMS.
phasor_from_p2p(A, θ) = phasor(A / √(2), θ)
phasor_from_p2p_deg(A, θ) = phasordeg(A / √(3), θ)


######################################################################
###################     IMPEDANCE     ################################
######################################################################

function parallel(Z1, Z2)
    return (1/Z1 + 1/Z2)^-1
end

function series(Z1, Z2)
    return Z1 + Z2
end

######################################################################
###################     POWER    #####################################
######################################################################

function pf_from_complex(S)
    return cos(angle(S))
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


######################################################################
########################     DISPLAY     #############################
######################################################################

function print_values(v)
    for (name, value) in pairs(v)
        println(name)
        display(round.(value, sigdigits=3))
    end
end

function Base.show(io::IO, x::Complex)
    x_ang = rad2deg(angle(x))
    print(io, "$(abs(x)) ∠ $(x_ang)° | $(real(x)) + j $(imag(x))")
end


# function print_value(val)
#     display(val)
# end

# function print_value(val::Complex)
#     print_phasor(val)
# end

# function print_value(val::Matrix)
# end


# function print_phasor(a, deg=true)
#     a_ang = angle(a)
#     if deg
#         a_ang = rad2deg(a_ang)
#     end
#     println("Phasor: $(abs(a)) ∠ $(a_ang)°")
#     println("Complex: $a")
# end


# function print_phasors(values)
#     for (name, v) in pairs(values)
#         println(name)
#         print_phasor(v)
#     end
# end


# function print_matrices(values; args...)
#     for (name, v) in pairs(values)
#         println(name)
#         display(round.(v; sigdigits=3, args...))
#     end
# end



end # module PowerSystems
