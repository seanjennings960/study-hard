import numpy as np
from numpy.polynomial import Polynomial as Poly
import sympy as sp
import control

sp.init_printing(use_unicode=True)

def pprint(A):
    print(A.table(sp.StrPrinter()))

def problem1a():
    A = np.array([
        [-1, 1/2, 1/2],
        [1/2, -1, 1/2],
        [1/2, 1/2, -1]
    ])
    lam, P = np.linalg.eig(A)
    A = sp.Matrix(A)
    P, J = A.jordan_form()
    print(P@J@P.inv())
    print(sp.exp(J))
    print(3 * P.inv().evalf(3))
    x = sp.symbols("x")
    D = sp.Matrix([
        [x, 0, 0],
        [0, x, 0],
        [0, 0, 1]
    ])
    print(P@D)
    print(3*P@D@P.inv())
    print(sp.exp(A).evalf(3))
    # print(sp.exp(A) @ sp.Matrix([1, 1/2, 0]))
    print(1/3 * (np.ones((3, 3)) + np.array([
        [2, -1, -1],
        [-1, 2, -1],
        [-1, -1, 2]
    ]) * np.exp(-1.5)))
    e_A = np.array(sp.exp(A)).astype(float)
    x_1_u = 1/3 * (
        np.ones(3) + 1/1.5 * np.array([2, -1, -1]) * (1 - np.exp(-1.5))
    )
    x0 = np.array([1, 1/2, 0])
    print("e_A x(0)", e_A @ x0)
    print("delta_u", x_1_u)
    x_1 = e_A @ x0 + x_1_u
    print("x_1", x_1)
    x_2 = e_A @ x_1 + 1/2 * x_1_u
    print("e_A x(1)", e_A @ x_1)
    print("x_2", x_2)
    e_A2 = np.array(sp.exp(2 * A)).astype(float)
    print(type(e_A2))
    print(e_A2.dtype)
    print("e_A2", np.round(e_A2, 3))
    print("e_A2 x(0)", np.round(e_A2 @ x0, 3))
    print("e_A2 x(0) + 3/2 delta_u", np.round(e_A2 @ x0 + (e_A + 1/2 * np.eye(3)) @ x_1_u, 3))


def problem1b():
    A = np.array([
        [-1, 1/2, 1/2],
        [1/2, -1, 1/2],
        [1/2, 1/2, -1]
    ])
    B = np.array([1, 0, 0])
    C1 = A @ B
    C2 = A @ A @ B
    print(C1)
    print(C2)

def problem2():
    C = np.array([
        [1, 1, 1],
        [0, -1, -2],
        [1, 1, 2]
    ])
    print(np.linalg.det(C))
    A = sp.Matrix([
        [1, 0, 0],
        [0, 1, -1],
        [0, -1, 1]
    ])
    s = sp.symbols('s')
    D = (s * sp.eye(3) - A).inv()
    pprint(D)


def problem3():
    A = np.array([
        [2, 0, 0],
        [0, -1, 1],
        [0, 0, -2]
    ])
    print(np.linalg.eigvals(A))
    p = Poly.fromroots(np.linalg.eigvals(A))
    print(p)
    B = np.array([1, 1, 0])
    K = np.array([-3, 0, 0])
    print(np.linalg.eigvals(A + np.outer(B, K)))

def problem4():
    L = np.array([
        [2, 1],
        [1, 3]
    ])
    A = np.array([
        [0, 1],
        [-1, 0]
    ])
    B = np.array([[0], [1]])
    R = np.array([1])
    print(np.linalg.eigvals(L))
    K, S, E = control.lqr(A, B, L, R)
    print("K", K)
    print("S", S)
    print("E", E)
    R_inv = np.linalg.inv([R])
    print("R_inv", R_inv)
    print("K_comp:", -R_inv @ B.T @ S)
    print("ARE sum:", A.T @ S + S @ A + L - S @ B @ R_inv @ B.T @ S)


    


def main():
    # problem1a()
    # problem1b()
    # problem2()
    problem4()


if __name__ == "__main__":
    main()