import math

import matplotlib.pyplot as plt
import numpy as np


class SolverResult:
    def __init__(self, root, success, steps):
        self.root = root
        self.success = success
        self.steps = steps


KNOWN_METHODS = ["newton", "modified_newton"]
VERY_SMALL = 1e-50

def find_root(f, f_prime, x0, tol, n_max, method="newton", root_multiplicity=None):
    """
    Find the root of the function using Newtons method.
    
    Input:
        f: function
        f_prime: derivative of f
        x0: initial guess
        tol: tolerance
        n_max: max iterations
        method: "newton" for standard newton's or "modified_newton" for modified
            version
        root_multiplicity: multiplicity of root to be used for modified method.

    outputs:
        SolverResult:
            root: found root of function
            success: True if tolerance was attained before maximum number of iterations.
            steps: x_n for each n in the iteration.
    """
    if method not in KNOWN_METHODS:
        raise ValueError(f"Unknown method: {method}. Accepted methods: {KNOWN_METHODS}")  # noqa
    if method == "modified_newton" and root_multiplicity is None:
        raise ValueError("root_multiplicity must be specified with modified newton method.") # noqa

    p = root_multiplicity

    steps = [x0]
    for _ in range(n_max):
        if method == "newton":
            x1 = x0 - f(x0) / f_prime(x0)
        elif method == "modified_newton":
            x1 = x0 - p * f(x0) / f_prime(x0)
        steps.append(x1)
        # Also add a stop condition when |f(x1)| is very small. 
        # This corresponds to the case where
        if abs(x1 - x0) < tol or abs(f(x1)) < VERY_SMALL:
            return SolverResult(x1, True, np.array(steps))
        x0 = x1
    return SolverResult(x1, False, np.array(steps))


def f(x):
    return (x - 1) ** 5 * np.exp(x)

def f_prime(x):
    return (x-1)**4 * np.exp(x) * ((x-1) + 5)

def f_pprime(x):
    return (x-1)**3 * np.exp(x) * ((x-1)**2 + 10 * (x-1) + 20)


def print_table(err, steps):
    print(f"k    x_k               Error")
    for i, (x_k, e) in enumerate(zip(steps, err)):
        if i > 20 and i %5 != 0:
            continue
        print(f"{str(i):<4}", f"{x_k:.10e}", f"{e:.10e}")

def problem_5():
    x0 = 0.001
    tol = 1e-15
    n_max = 100
    result = find_root(f, f_prime, x0, tol, n_max, "modified_newton", 5)
    err = np.abs(1 - result.steps)
    print_table(err, result.steps)

    fig = plt.figure()
    plt.semilogy(err)
    plt.xlabel("Iteration k")
    plt.ylabel("Iteration k")
    fig.savefig("tex/hw3/Images/modified_newtons_plot.png")
    plt.show()

    result = find_root(f, f_prime, x0, tol, n_max, "newton", 5)
    err = np.abs(1 - result.steps)
    print_table(err, result.steps)
    fig = plt.figure()
    plt.semilogy(err)
    plt.xlabel("Iteration k")
    plt.ylabel("log(error)")
    plt.show()
    fig.savefig("tex/hw3/Images/newtons_plot.png")

###########################################
# Bisection code from HW2
###########################################


EXIT_SUCCESS = 0
EXIT_FAILURE = 1


class BisectionResult:
    def __init__(self, root, exit_status, steps):
        self.root = root
        self.exit_status = exit_status
        self.steps = steps


def bisection(f, a, b, atol):
    steps = [a]
    fa = f(a)
    fb = f(b)
    if fa * fb > 0:
        return BisectionResult(
            a, EXIT_FAILURE, steps
        )

    while abs(a - b) > atol:
        c = 1/2 * (a + b)
        fc = f(c)
        if fa * fc < 0:
            b = c
        else:
            a = c
            fa = fc
        steps.append(a)
    return BisectionResult(
        a, EXIT_SUCCESS, steps
    )

###########################################
# Problem 2
###########################################

ALPHA = 0.138e-6  # m^2 / second
T_s = -15  # degree Celsius
T_i = 20  # degree Celsius
T0 = 60 * 3600 * 24  # seconds


def f2(x):
    return math.erf(x / 2 / math.sqrt(ALPHA * T0)) + T_s / (T_i - T_s)

def f2_prime(x):
    return 2 / math.sqrt(math.pi) * math.exp(- x**2 / 4 / ALPHA / T0)


def problem_2():
    x_bar = 10

    x = np.linspace(0, x_bar, 1000)
    fig = plt.figure()
    plt.plot(x, [f2(x_i) for x_i in x])
    plt.xlabel("Distance underground (meters)")
    plt.ylabel("f(x)")
    fig.savefig("tex/hw3/Images/temp_plot.png")
    plt.show()
    tol = 1e-13
    result = bisection(f2, 0, x_bar, tol)
    print(f"Bisection outcome = {result.exit_status}")
    print(f"root: {result.root}")
    print(f"number of iterations: {len(result.steps)}")

    x0 = 0.01
    newton_result = find_root(f2, f2_prime, x0, tol, 100)
    print("With x0=0.01")
    print(f"Newton converged:  {newton_result.success}")
    print(f"Newton root:  {newton_result.root}")
    print(f"number of iterations: {len(newton_result.steps)}")

    x0 = x_bar
    newton_result = find_root(f2, f2_prime, x0, tol, 100)
    print("With x0=0.01")
    print(f"Newton converged:  {newton_result.success}")
    print(f"Newton root:  {newton_result.root}")
    print(f"number of iterations: {len(newton_result.steps)}")

if __name__ == '__main__':
    problem_5()
