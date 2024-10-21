import numpy as np


def round_to_sigfig(x, sigfig=4):
    if x == 0:
            return 0
    return np.float64(np.round(x, sigfig - int(np.floor(np.log10(abs(x)))) - 1))

def round_array(A, sigfig=4):
    B = np.zeros_like(A)
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            B[i,j] = round_to_sigfig(A[i,j], sigfig)

    return B

def problem3():
    A = np.array([
        [6, 2, 2, -2],
        [2, 2/3, 1/3, 1],
        [1, 2, -1, 0]
    ])
    A = round_array(A)
    print(A)

    n = A.shape[0]
    pivot = True

    for i in range(0, n-1):
        if pivot:
            largest_row = i + np.argmax(A[i:, i])
            if largest_row != i:
                print(f"Swapping rows {i} and {largest_row}")
                temp = np.copy(A[i])
                A[i] = A[largest_row]
                A[largest_row] = temp
        for j in range(i+1, n):
            mult = round_to_sigfig(A[j, i] / A[i, i])
            A[j, :] = A[j, :] - mult * A[i, :]
            print(f"Step ({i}, {j})")
            print(f"multiplier: {mult}")
            # print(A)
            A = round_array(A)
            print("Rounded:")
            print(round_array(A))


    x = np.zeros((n, 1))
    y = A[:, -1]
    for k in range(n-1, -1, -1):
        partial = 0
        for i in range(k+1, n):
            partial += round_to_sigfig(A[k, i] * x[i])
            partial = round_to_sigfig(partial)
            print(f"Partial (i,k) = ({i}, {k}): {partial}")
        x[k] = round_to_sigfig(round_to_sigfig(y[k] - partial) / A[k, k])
        print(f"x[{k}]: {x[k]}")
    print("x:", x)


def spectral_radius(A):
    return max(np.abs(np.linalg.eigvals(A)))


def gauss_jacobi(A, b, x0, tol, max_iter):
    D = np.diagflat(np.diag(A))
    LU = A - D

    D_inv = np.linalg.inv(D)

    rho = spectral_radius(D_inv @ LU)
    for it in range(max_iter):
        x1 = - D_inv @ LU @ x0 + D_inv @ b

        err = np.linalg.norm(A @ x1 - b)
        if err < tol:
            print(f"rho(B) = {rho}")
            rhs = rho / (1 - rho) * np.linalg.norm(x1 - x0)
            print(f"(c / (1 - c) * |x_(k+1) - x_k| = {rhs}")
            return x1, "success", it
        x0 = x1

    return x0, "failure", max_iter

def gauss_seidel(A, b, x0, tol, max_iter):
    M = np.tril(A)
    N = np.triu(A, 1)
    M_inv = np.linalg.inv(M)

    rho = spectral_radius(M_inv @ N)
    for it in range(max_iter):
        x1 = - M_inv @ N @ x0 + M_inv @ b

        err = np.linalg.norm(A @ x1 - b)
        if err < tol:
            print(f"rho(B) = {rho}")
            rhs = rho / (1 - rho) * np.linalg.norm(x1 - x0)
            print(f"(c / (1 - c) * |x_(k+1) - x_k| = {rhs}")
            return x1, "success", it
        x0 = x1

    return x0, "failure", max_iter

def sor(A, b, x0, omega, tol, max_iter):
    D = np.diagflat(np.diag(A))
    L = np.tril(A, -1)
    U = np.triu(A, 1)
    M = D + omega * L
    N = (1 - omega) * D - omega * U

    M_inv = np.linalg.inv(M)

    rho = spectral_radius(M_inv @ N)
    for it in range(max_iter):
        x1 = M_inv @ N @ x0 + omega * M_inv @ b
        err = np.linalg.norm(A @ x1 - b)
        if err < tol:
            print(f"rho(B) = {rho}")
            rhs = rho / (1 - rho) * np.linalg.norm(x1 - x0)
            print(f"(c / (1 - c) * |x_(k+1) - x_k| = {rhs}")
            return x1, "success", it
        x0 = x1

    return x0, "failure", max_iter



def problem4():
    A =  np.array([
        [4, -1, 0, -1, 0, 0],
        [-1, 4, -1, 0, -1, 0],
        [0, -1, 4, -1, 0, -1],
        [-1, 0, -1, 4, -1, 0],
        [0, -1, 0, -1, 4, -1],
        [0, 0, -1, 0, -1, 4],
    ])
    b = np.array([2, 1, 2, 2, 1, 2])
    x0 = np.ones(6)
    max_iter = 1000
    tol = 1e-7
    x_sol, outcome, iters = gauss_jacobi(A, b, x0, tol, max_iter)
    if outcome == "success":
        print(f"Gauss-Jacobi converged to {x_sol} in {iters} iterations")
    else:
        print("Gauss-Jacobi failed to converge")

    x_sol, outcome, iters = gauss_seidel(A, b, x0, tol, max_iter)
    if outcome == "success":
        print(f"Gauss-Seidel converged to {x_sol} in {iters} iterations")
    else:
        print("Gauss-Seidel failed to converge")

    # omega = 1.6735
    for omega in [-0.25, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.6735, 1.75, 2.1]:
        x_sol, outcome, iters = sor(A, b, x0, omega, tol, max_iter)
        print(f"omega = {omega}")
        if outcome == "success":
            print(f"SOR converged to {x_sol} in {iters} iterations")
        else:
            print("SOR failed to converge")


def main():
    problem4()


if __name__ == '__main__':
    main()
