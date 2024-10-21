import math
import numpy as np
import matplotlib.pyplot as plt

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


class BisectionResult:
    def __init__(self, root, exit_status):
        self.root = root
        self.exit_status = exit_status


def bisection(f, a, b, atol):
    fa = f(a)
    fb = f(b)
    if fa * fb > 0:
        return BisectionResult(
            a, EXIT_FAILURE
        )

    while abs(a - b) > atol:
        c = 1/2 * (a + b)
        fc = f(c)
        if fa * fc < 0:
            b = c
        else:
            a = c
            fa = fc
    return BisectionResult(
        a, EXIT_SUCCESS
    )


def f1(x):
    return (x - 5)**9

N = 9
COEFFICIENTS = [math.comb(N, k) * (-5)**(N-k) for k in range(0, N+1)]

def f2(x):
    return sum([coef * x ** k for k, coef in enumerate(COEFFICIENTS)])


def main():
    print("Coefficients: ", COEFFICIENTS)  # noqa
    a = 4.8
    b = 5.31
    tol = 1e-4
    res = bisection(f1, a, b, tol)
    print("Bisection return status for (x-5)^9:", res.exit_status)  # noqa
    print("Bisection root for (x-5)^9:", res.root)  # noqa
    res = bisection(f2, a, b, tol)
    print("Bisection return status for expansion:", res.exit_status)  # noqa
    print("Bisection root for expansion:", res.root)  # noqa
    # for v in [a, b, 5, 5.02, 4.98]:
    x = np.linspace(4.85, 5.15, 500)
    y_f1 = [f1(v) for v in x]
    y_f2 = [f2(v) for v in x]
    fig = plt.figure(figsize=(10,3))
    plt.plot(x, y_f1, label="(x-5)^9")
    plt.plot(x, y_f2, label="Binomial expansion")
    plt.legend()
    plt.xlabel("x")
    plt.ylabel("f(x)")
    fig.savefig("tex/hw2/Images/f1_vs_f2.png")
    plt.show()
    # for v in np.linspace(a, b, 1000):
    #     print(f"f1({v}):", f1(v))  # noqa
    #     print(f"f2({v}):", f2(v))  # noqa
    print([f"{coef * a ** k:.2e}" for k, coef in enumerate(COEFFICIENTS)])




if __name__ == "__main__":
    main()
