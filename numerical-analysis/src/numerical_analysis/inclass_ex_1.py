import itertools

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

CMAP = mpl.colormaps["magma"]


def _lagrange_basis(x, j):
    """Return the j-th Lagrange basis function for nodes x"""
    N = len(x)
    def l_j(x_in):
        prod = np.ones_like(x_in)
        for i in itertools.chain(range(j), range(j+1, N)):
            prod *= (x_in - x[i]) / (x[j] - x[i])
        return prod
    return l_j


def lagrange_polynomial(x, f):
    """
    Create a polynomial which interpolates between each point (x[i], f[i])
    """
    N = len(x)
    if len(f) != N:
        err = "x and f must be 1-dim vectors with same length."
        raise ValueError(err)
    l_basis = [_lagrange_basis(x, j) for j in range(len(x))]

    def p(x_in):
        # x_in can be a scalar or array of length M.
        # the list comprehension is stored as either
        # a (N,) array or (N, M). Sum over the first axis
        # in either case.
        return np.sum([l_basis[j](x_in) * f[j]
                       for j in range(N)], axis=0)
    return p


def scale(x, c, d):
    a = x[0]
    b = x[-1]
    alpha = (d - c) / (b - a)
    beta = (b * c - a * d) / (b - a)
    return alpha * x + beta

def plot_lagrange_interp(func, x_range, *, spacing="linear", p_max=21, plot_error=True):
    if spacing not in ["linear", "chebychev"]:
        raise ValueError('spacing must be "chebychev" or "linear"')  # noqa


    x_eval = np.linspace(*x_range, 1000)
    plt.figure()
    if not plot_error:
        plt.plot(x_eval, func(x_eval), label="True function")
    for n_points in range(2, p_max):
        if spacing == "linear":
            x = np.linspace(*x_range, n_points)
        else:
            js = np.arange(0, n_points+1)
            x = np.cos((2 * js + 1) * np.pi / (2 * (n_points + 1)))
            # Flip direction so x is increasing.
            x = x[::-1]
            x = scale(x, x_range[0], x_range[1])
            print(f"range of x: {min(x)}, {max(x)})")

        f = func(x)
        p = lagrange_polynomial(x, f)
        color = CMAP(n_points / p_max)
        if plot_error:
            err = np.abs(func(x_eval) - p(x_eval))
            plt.semilogy(x_eval, err, color=color, label=f"Error (P={n_points})")
        else:
            plt.plot(x_eval, p(x_eval), color=color, label=f"Interpolant (P={n_points})")

    plt.legend()
    plt.xlabel("x")
    plt.ylabel("Error |f(x) - p(x)|")

def problem1():

    # plot_lagrange_interp(np.exp, (0, 1))
    # plt.title("Lagrange interpolation error for e^x")
    # plt.show()

    def f2(x):
        return 1 / (1 + x**2)

    # plot_lagrange_interp(f2, [-5, 5])
    # plt.title("Lagrange interpolation error for 1/(1+x^2)")
    # plt.show()

    # plot_lagrange_interp(f2, [-5, 5], p_max=10, plot_error=False)
    # plt.title("Lagrange interpolation error for 1/(1+x^2)")
    # plt.show()

    plot_lagrange_interp(f2, [-5, 5], spacing="chebychev",
                         p_max=10, plot_error=False)
    plt.title("Chebychev interpolation for 1/(1+x^2)")
    plt.show()

    plot_lagrange_interp(f2, [-5, 5], spacing="chebychev",
                         p_max=15, plot_error=True)
    plt.title("Chebychev interpolation error for 1/(1+x^2)")
    plt.show()

    def f3(x):
        return np.where(x<=0, 1, 0)

    for spacing in ["linear", "chebychev"]:
        for plot_error in [False, True]:
            p_max = 30 if plot_error else 30
            plot_lagrange_interp(f3, [-1, 1], spacing=spacing,
                                p_max=p_max, plot_error=plot_error)
            plt.title(f"{spacing} | {'error' if plot_error else 'function'}")
        plt.show()



def main():
    problem1()


if __name__ == "__main__":
    main()
