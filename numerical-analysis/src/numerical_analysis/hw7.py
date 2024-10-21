import matplotlib.pyplot as plt
import numpy as np

ERR_MAX = 1e64  # Divergence threshold

def steepest_descent(A, b, x0, tol, N_max=1000):
    # Perform steepest descent algorithm to solve linear system Ax = b
    # Inputs:
    #  A: symmetric positive definite (NxN) matrix in Ax = b
    #  b: RHS N-dim vector in Ax = b #  x0: initial guess shape (N,)
    #  tol: tolerance
    # N_max: maximum number of iterations
    # Returns:
    #   tuple (x_sol, ier, history) where
    #  x_sol = solution
    #  ier (bool) = whether steepest descent converged
    #  history = (M+1, N) array of the iterate x_k on each iteration
    #       (M = number of iterations required to converge within tol,
    #        i.e. if initial guess is within tolerance, then M=0 and history
    #        only contains initial guess.)
    N = A.shape[0]
    history = np.zeros((N_max+1, N))
    history[0, :] = x0
    for k in range(1, N_max + 1):
        g0 = A @ x0 - b
        err = np.linalg.norm(g0)
        if err < tol:
            # Converged on the previous iteration
            return x0, True, history[:k]
        elif err > ERR_MAX:
            # algorithm has diverged.
            return x0, False, history[:k]
        alpha = g0.T @ g0 / (g0.T @ A @ g0)
        x1 = x0 - alpha * g0
        history[k, :] = x1
        x0 = x1
    return x0, False, history


def conjugate_gradient(A, b, tol, N_max=1000):
    N = A.shape[0]
    x0 = np.zeros(N)
    r0 = b - A @ x0
    p0 = r0
    history = np.zeros((N_max+1, N))
    history[0, :] = x0
    for k in range(1, N_max + 1):
        r0 = b - A @ x0
        err = np.linalg.norm(r0)
        if err < tol:
            return x0, True, history[:k]
        elif err > ERR_MAX:
            # algorithm has diverged.
            return x0, False, history[:k]

        # Perform iteration
        alpha = (r0.T @ r0) / (r0.T @ A @ r0)
        x1 = x0 + alpha * p0
        r1 = b - A @ x1
        beta = - (r1.T @ r1) / (p0.T @ (r0 - r1))
        # beta = - (p0.T @ A @ r1) / (p0.T @ A @ p0)
        p1 = r1 + beta * p0

        # Update previous guesses
        p0 = p1
        x0 = x1
        history[k, :] = x1
    return x0, False, history


def create_matrix(N, tau):
    A = np.random.uniform(-1, 1, (N, N))
    for i in range(N):
        for j in range(i):
            # For each j (0 <= j < i), copy the upper
            # diagonal entry (j, i) to the lower diagonal
            # to ensure symmetry.
            A[i, j] = A[j, i]

    A[abs(A) > tau] = 0

    # Set diagonals to 1.
    for i in range(N):
        A[i, i] = 1

    return A

def main():

    np.random.seed(10)

    N = 500
    tol = 1e-10
    # x0 = np.zeros(N)

    b = np.random.uniform(0, 10, N)
    x0 = b
    taus = np.array([0.01, 0.05, 0.1, 0.2])
    As = [create_matrix(N, tau) for tau in taus]
    residual_norms = []

    for A in As:
        x_sol, success, history = steepest_descent(A, b, x0, tol)
        if success:
            print(f"Converged in {len(history)} iterations")
        else:
            print("Failed to converge")

        residual_norms.append(np.linalg.norm(b[:, np.newaxis] - A @ history.T, axis=0))

    plt.figure()
    for tau, res in zip(taus, residual_norms):
        plt.semilogy(res, label=f"tau={tau}")
    plt.legend()
    plt.xlabel("Iteration index (k)")
    plt.ylabel("|r_k| (norm-2 of residual)")
    plt.title("Residual versus iteration for Steepest Descent")
    plt.show()

    # Evaluate conjugate gradient algorithm
    residual_norms = []
    for A in As:
        print(f"Condition number of A: {np.linalg.cond(A)}")
        x_sol, success, history = conjugate_gradient(A, b, tol)
        if success:
            print(f"Converged in {len(history)} iterations")
        else:
            print("Failed to converge")

        residual_norms.append(np.linalg.norm(b[:, np.newaxis] - A @ history.T, axis=0))

    plt.figure()
    for tau, res in zip(taus, residual_norms):
        plt.semilogy(res, label=f"tau={tau}")
    plt.legend()
    plt.xlabel("Iteration index (k)")
    plt.ylabel("|r_k| (norm-2 of residual)")
    plt.title("Residual versus iteration for Conjugate Gradient")
    plt.show()


def problem3():
    e0 = 1
    e10 = 2 * (2**-10)
    B = (e10 / 2 * e0)**(1/10)
    kappa_upper = ((1 + B) / (1 - B))**2
    print("Kappa upper bound:", kappa_upper)

    c = np.sqrt(1 / kappa_upper)
    e20_bound = 2 * ((1 - c) / (1 + c))**20
    print(f"e20 bound: {e20_bound}")

def problem2_error_bound():
    kappa = 10
    for kappa in [1.063, 1.851, 10, 8500]:
        c = np.sqrt(1 / kappa)
        per_iter_bound = 2 * ((1 - c) / (1 + c))
        print(f"Per iteration bound (kappa = {kappa}):", per_iter_bound)




if __name__ == "__main__":
    problem3()
