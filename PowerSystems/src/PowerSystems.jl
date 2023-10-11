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

function S_from_P_pf(P, pf, leading)
    dir = if leading; -1 else 1 end
    Q = P * tan(dir * acos(pf))
    return P + im * Q
end



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
###################     SEQUENCE    ##################################
######################################################################

# TODO: Figure out how to either name these better or put them
# inside of a class so it doesn't leak these super generic names!
# Well, really there should be a nicer interface than just
# pure matrices??
a = phasordeg(1, 120)
A = [
    1 1 1
    1 a^2 a
    1 a a^2
]
# Line-to-line conversion
B = [
    1 -1 0
    0 1 -1
    -1 0 1
]

######################################################################
########################     DISPLAY     #############################
######################################################################

DISPLAY_SIGDIGITS = 4

function print_values(v::NamedTuple)
    for (name, value) in pairs(v)
        println(name)
        print_value(value)
    end
end

function print_value(v)
    display(round.(v, sigdigits=DISPLAY_SIGDIGITS))
end

function print_value(v::Complex)
    # Rounding for complex is done inside show! (Will also need to extend
    # to complex matrices..)
    display(v)
end

function Base.show(io::IO, x::Complex)
    x_real = round(real(x), sigdigits=DISPLAY_SIGDIGITS)
    x_imag = round(imag(x), sigdigits=DISPLAY_SIGDIGITS)
    x_abs = round(abs(x), sigdigits=DISPLAY_SIGDIGITS)
    x_ang = round(rad2deg(angle(x)), sigdigits=DISPLAY_SIGDIGITS)
    print(io, "$(x_abs) ∠ $(x_ang)° | $(x_real) + j $(x_imag)")
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
