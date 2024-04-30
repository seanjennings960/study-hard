import numpy as np


# CH 3
def sqrt_difference(n):
    return np.sqrt(n + 1) - np.sqrt(n)

def over_n(n):
    return (np.sqrt(n+1) - np.sqrt(n)) / n

def sum(func, n):
    return np.sum(func(np.arange(1, n)))

def ratio_test(func, n):
    return np.abs(func(n+1) / func(n))


def root_test(func, n):
    return func(n) ** (1/n)

def problem_6():
    for n in [100, 10_000, int(1e6)]:
        print(f"Square root difference (n={n}): {sum(sqrt_difference, n)}")

    for n in [100, 10_000, int(1e6), ]: # int(1e8)
        print(f"over_n (n={n}): {sum(over_n, n)}")

    print("Over_n eval (n=10_000):", over_n(10_000))
    print("Over_n ratio:", ratio_test(over_n, 10_000))
    print("Over_n root:", root_test(over_n, 10_000_000))


def main():
    problem_6()


if __name__ == '__main__':
    main()