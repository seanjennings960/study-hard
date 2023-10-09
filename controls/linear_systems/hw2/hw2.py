import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

def print_matrix_latex(a):
    rows = [" & ".join([str(entry) for entry in a.row(i)])
            for i in range(a.rows)]
    print("  \\\\\n".join(rows))

def problem1_2():
    B = sp.Matrix([
        [-1, 1, 0],
        [1/2, -1, 1/2],
        [0, 1, -1]
    ])
    P, J = B.jordan_form()
    print("P, J")
    print((P, J))
    e_B_man = P * sp.exp(J) * P.inv()
    print("P^-1")
    print_matrix_latex(P.inv().evalf(3))

    print('e^J')
    print((J.exp(),))
    print('e_B_man')
    print((e_B_man.evalf(3),))
    print_matrix_latex(e_B_man.evalf(3))
    print('e_B')
    print((B.exp(),))

def phi_1_3(t):
    return sp.Matrix([
        [sp.exp(t) * sp.cos(2*t), sp.exp(-2*t) * sp.sin(2*t)],
        [-sp.exp(t) * sp.sin(2*t), sp.exp(-2*t) * sp.cos(2*t)],
    ])

def problem1_3():
    x = phi_1_3(2) * phi_1_3(1).inv()

    print('Phi(2, 0)')
    print_matrix_latex(phi_1_3(2).evalf(3))
    print('Phi(1, 0)')
    print_matrix_latex(phi_1_3(1).evalf(3))
    print('Phi(0, 1)')
    print_matrix_latex(phi_1_3(1).inv().evalf(3))
    print('Phi(2, 1)')
    print_matrix_latex(x.evalf(3))
    print('Phi(2, 0) (check)')
    print_matrix_latex((x * phi_1_3(1)).evalf(3))

def problem_4_1():
    A = sp.Matrix([
        [-3, 0, 0],
        [1, -5, 6],
        [2, 5, -6]
    ])
    P, J = A.jordan_form()
    print('P')
    print_matrix_latex(P.evalf(3))
    print('J')
    print_matrix_latex(J.evalf(3))

def alpha_to_lambda(alpha):
    tr = alpha * ( alpha - 1)
    det = alpha

    return (1/2 * (tr + np.sqrt(np.complex128(
        tr**2 - 4 * det
    ))),
    1/2 * (tr - np.sqrt(np.complex128(
        tr**2 - 4 * det
    ))))

def problem_4_2():
    alpha = np.linspace(-5, 5, 1000)

    start, end = -1., 2.35
    fig = plt.figure()
    for i, (alpha, label, marker) in enumerate([
        (np.array([start]), f"α = {start}", 'o'),
        (np.linspace(start, 0, 100), f"{start} < α < 0", None),
        (np.array([0.]), "α = 0", 'o'),
        (np.linspace(0, 1, 100), "0 < α < 1", None),
        (np.array([1.]), "α = 1", 'o'),
        (np.linspace(1, end, 10000), f"1 < α < {end}", None),
        (np.array([end]), f"α = {end}", 'o'),
    ]):
        x1, x2 = alpha_to_lambda(alpha)
        plt.plot(np.real(x1), np.imag(x1), label=label, marker=marker, c=f"C{i}")
        plt.plot(np.real(x2), np.imag(x2), marker=marker, c=f"C{i}")
    
    plt.grid()
    plt.legend()
    plt.title("Eigenvalue in complex plane")
    plt.xlabel("Real(λ)")
    plt.ylabel("Imaginary(λ)")
    plt.show()
    fig.savefig("eigenvalues.png")



    

if __name__ == '__main__':
    problem1_2()