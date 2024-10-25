import numpy as np


def problem1():
    x = np.array([60, 80, 70, 100, 130, 40, 30])
    print(np.sum(x))
    print(np.mean(x))
    N = len(x)
    var_i = (x - np.mean(x))**2
    print(var_i)
    var = np.sum((x - np.mean(x))**2) / (N-1)
    print(f"Variance: {var}")
    print(f"std: {np.sqrt(var)}")
    print(f"std/sqrt(N): {np.sqrt(var) / np.sqrt(N)}")
    print(f"var/sqrt(3): {var / np.sqrt(3)}")
    print(f"R(0): {np.sum(x ** 2) / N}")
    print(f"R(1): {np.sum(x[:-1] * x[1:]) / (N-1)}")
    print(f"R(2): {np.sum(x[:-2] * x[2:]) / (N-2)}")


def main():
    problem1()

if __name__ == "__main__":
    main()
