import numpy as np

def print_power(P, n, figs=4):
    print(np.round(np.linalg.matrix_power(P, n), 4))

def problem6():
    P = np.array([
        [1, 0, 0, 0, 0],
        [1/4, 0, 3/4, 0, 0],
        [0, 1/4, 0, 3/4, 0],
        [0, 0, 1/4, 0, 3/4],
        [0, 0, 0, 0, 1]
    ])
    print(128 * np.linalg.matrix_power(P, 4))
    print(np.round(np.linalg.matrix_power(P, 100), 3))


def problem7():
    P = np.array([
        [0, 1, 0, 0, 0],
        [1/3, 0, 2/3, 0, 0],
        [0, 1/2, 0, 1/2, 0],
        [0, 0, 2/3, 0, 1/3],
        [0, 0, 0, 1, 0]
    ])
    print(np.round(np.linalg.matrix_power(P, 4), 4))

def problem8():
    P = np.array([
        [0, 1/2, 1/2],
        [0.1, 0.7, 0.2],
        [0.2, 0.8, 0]
    ])
    print_power(P, 7)
    print("50")
    print_power(P, 50)

def main():
    problem8()


if __name__ == '__main__':
    main()