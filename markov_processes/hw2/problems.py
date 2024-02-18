import numpy as np
from numpy import log, linspace
from numpy.random import uniform
import matplotlib.pyplot as plt

def histogram(z, **kwargs):
    bin_heights, bins, patch = plt.hist(z, **kwargs)
    if kwargs.get("range") is None:
        return bin_heights, bins, patch
    # Fix matplotlib's buggy histogram normalization:
    # they display P("Z in bin" | "Z in range")
    # which overestimates the probability that Z is in a given
    # bin since it neglects 
    min_z, max_z = kwargs["range"]
    p_in_range = np.sum((min_z <= z) & (z <= max_z)) / len(z)
    print('P in range:', p_in_range)
    for rectangle in patch.patches:
        height = rectangle.get_height()
        rectangle.set_height(height * p_in_range)
    return bin_heights, bins, patch



def exponential(lambda_, n):
    # Generate (n,) array of uniform RVs.
    u = uniform(0, 1, n)
    # Compute exponential via inverse transform method.
    return -1/lambda_ * log(u)

def problem5():
    N = 100_000
    lambda_1 = 1
    lambda_2 = 2
    max_z = 4
    # Sample X, Y from exponential distrution (with N datapoints) and 
    # perform element-wise division to compute Z.
    x = exponential(lambda_1, N)
    y = exponential(lambda_2, N)
    z = y / x
    # Compute analytically determined PDF.
    z_pdf = linspace(0, max_z)
    f_z = lambda_1 * lambda_2/ (lambda_1 + lambda_2 * z_pdf)**2

    fig = plt.figure()
    histogram(z, range=(0, max_z), density=True, bins=500)
    plt.plot(z_pdf, f_z)

    plt.xlabel("Z")
    plt.ylabel("f(Z)")
    plt.title("Z = Y/X, X~Exponential(1) | Y~Exponential(2)")
    plt.legend(["Analytic", f"Sampled (N={N})"])

    fig.savefig("Images/problem5.png")

    plt.show()



def problem6():
    N = 10_000
    x_max = 4
    # Sample Uniform distribution with N data points
    u = uniform(0, 1, N)
    # Simulate X using inverse tranform method.
    x = 1 / u ** (1/3)
    # Compute PDF over range
    x_range = np.linspace(1, x_max)
    f_x = 3 / x_range**4

    # Plot histogram of sampled points alongside PDF.
    fig = plt.figure()
    histogram(x, density=True, range=(1, x_max), bins=100, edgecolor='black')
    plt.plot(x_range, f_x)

    plt.title("Power-law RV | f(x) = 3x^-4")
    plt.xlabel("X")
    plt.ylabel("f(x)")
    plt.legend(["Analytic", "Sampled"])
    
    # Display results
    print(f"Mean: {np.mean(x)}")
    # fig.savefig("Images/problem6.png")

    plt.show()


def main():
    problem4()


if __name__ == "__main__":
    main()