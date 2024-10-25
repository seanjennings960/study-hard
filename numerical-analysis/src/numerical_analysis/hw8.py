import numpy as np
import matplotlib.pyplot as plt

A = np.array([
    [0.016, -0.17],
    [0.52, -0.26]
])

ITER_MAX = 1e64  # Iteration divergence threshold


def f_1(z):
    x = z[0]
    y = z[1]
    return np.array([
        3 * x**2 + 4 * y**2 - 1,
        y**3 - 8 * x**3 - 1
    ])


def fp_iter_1(x):
    return x - A @ f_1(x)

def grad_g(z):
    x = z[0]
    y = z[1]
    return np.eye(2) - A @ np.array([
        [6 * x, 8 * y],
        [-24 * x **2, 3 * y ** 2]
    ])

def fixed_point_solve(g, x0, N_max, tol, ord=None):

    history = [x0]
    for _ in range(N_max):
        x1 = g(x0)
        history.append(x1)
        err = np.linalg.norm(x1 - x0, ord=ord)
        if err <= tol:
            return x1, True, history
        elif err > ITER_MAX:
            return x1, False, history
        x0 = x1
    return x1, False, history


def problem1():
    tol = 1e-7
    x0 = np.array([-0.5, 0.25])
    x_sol, converged, steps = fixed_point_solve(fp_iter_1, x0, 1000, tol)
    if converged:
        print(f"Converged to {x_sol} after {len(steps) - 1} steps")
    else:
        print("Fixed point iteration diverged")

    grad_g_0 = grad_g(x0)
    grad_g_sol = grad_g(x_sol)
    print("grad g(x0) = ")
    print(grad_g_0)
    sigmas = np.linalg.svd(grad_g_0, compute_uv=False)
    print(f"singular values: {sigmas}")
    print("grad g(x_sol) = ")
    print(grad_g_sol)
    sigmas = np.linalg.svd(grad_g_sol, compute_uv=False)
    print(f"singular values: {sigmas}")


def g2(z, h):
    x = z[0]
    y = z[1]
    return np.array([
        1 + h**2 * (np.exp(y * np.sqrt(x)) + 3 * x**2),
        0.5 + h**2 * np.tan(np.exp(x) + y**2)
    ])


def sec2(x):
    return 1 / np.cos(x)**2

def jac_g2(z, h):
    x = z[0]
    y = z[1]
    e_to_y_root_x = np.exp(y * np.sqrt(x))
    sec2_exp = sec2(np.exp(x) + y**2)
    return h**2 * np.array([
        [y / (2 * np.sqrt(x)) * e_to_y_root_x + 6 * x,
            np.sqrt(x) * e_to_y_root_x],
        [np.exp(x) * sec2_exp, 2 * y * sec2_exp]
    ])

def inf_norm(A):
    """Return max row sum of abs(A)"""
    return np.max(np.sum(np.abs(A), axis=1))



def problem2():
    x0 = np.array([1, 0.5])

    for h in [0, 0.01, 0.1, 0.2, 0.22, 0.25, 0.3, 0.5, 1]:
        print(f"h: {h}")
        g = lambda x: g2(x, h)
        tol = 0.1 * h**4
        x_sol, converged, history = fixed_point_solve(g, x0, 1000, tol)
        if converged:
            print(f"Converged to {x_sol} after {len(history) - 1} iterations")
        else:
            print("Diverged")


        jac_at_fp = jac_g2(x_sol, h)
        print(f"Jacobian: {jac_at_fp}")
        print(f"inf_norm(Jacobian): {inf_norm(jac_at_fp)}")




def problem4():
    pts = np.array([
        (0, 0),
        (0, 2),
        (1, 0),
        (1, 2),
        (2, 1),
        (2, 3)
    ])
    A = np.array([
        [1, x, y, x * y, x**2, y**2] for x, y in pts
    ])
    f = np.exp(pts[:, 0]) * np.sin(pts[:, 1])
    c = np.linalg.solve(A, f)
    print(c)

    X, Y = np.meshgrid(np.linspace(-1, 3, 25), np.linspace(-1, 3, 25))
    z = np.exp(X) * np.sin(Y)
    p_z = c[0] + c[1] * X + c[2] * Y + c[3] * X * Y + c[4] * X**2 + c[5] * Y**2
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    p1 = ax1.pcolormesh(X, Y, z)
    p2 = ax2.pcolormesh(X, Y, p_z)
    p3 = ax3.pcolormesh(X, Y, z - p_z)

    fig.colorbar(p1, ax=ax1)
    fig.colorbar(p2, ax=ax2)
    fig.colorbar(p3, ax=ax3)
    for (x, y) in pts:
        ax2.plot(x, y, "ro")
        ax3.plot(x, y, "ro")
    ax3.set_xlabel("x")
    for ax in [ax1, ax2, ax3]:
        ax.set_ylabel("y")
    ax1.set_title("True function")
    ax2.set_title("Interpolated")
    ax3.set_title("Residual (true - interp)")
    # plt.colorbar()
    plt.show()







def main():
    problem4()


if __name__ == "__main__":
    main()
