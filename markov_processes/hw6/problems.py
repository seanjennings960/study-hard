import numpy as np
import matplotlib.pyplot as plt


def stationary_distribution(p):
    lambdas, vec = np.linalg.eig(p.T)
    # Find index where eigenvalue is 1.
    eig_1 = np.argwhere(np.isclose(lambdas, 1))
    # Reducible matrices have eigenvalue 1 with multiplicity >1.
    assert len(eig_1) == 1, "Probability matrix must be irreducible."
    column = eig_1[0, 0]
    stationary_dist = vec[:, column]
    # Make sure eigenvector is purely real.
    assert np.all(np.isclose(np.imag(stationary_dist), 0)), "Perron frobenius violation"
    stationary_dist /= np.sum(stationary_dist)
    return np.real(stationary_dist)


def problem_3():
    p = np.array([
        [0, 1, 0, 0, 0],
        [1/3, 0, 2/3, 0, 0],
        [0, 1/2, 0, 1/2, 0],
        [0, 0, 2/3, 0, 1/3],
        [0, 0, 0, 1, 0]
    ])
    q_0 = np.array([0, 1, 0, 0, 0])
    q_100 = q_0 @ np.linalg.matrix_power(p, 100)
    print("q_100")
    print(q_100)
    q_theoretical = np.array([1/12, 1/4, 1/3, 1/4, 1/12])

    fig = plt.figure()
    plt.plot(q_100, label='q_100')
    plt.plot(q_theoretical, label="pi (stationary dist)")
    plt.xlabel("i")
    plt.ylabel("Probability of state i")
    plt.title("q_100 and pi vs state i")
    fig.savefig("Images/q_100.png")
    plt.show()

def problem_4():
    p = np.array([
        [0.9, 0.06, 0.04],
        [0.1, 0.85, 0.05],
        [0.2, 0.1, 0.7]
    ])
    pi = stationary_distribution(p)
    print(f"Stationary dist: {np.round(pi, 4)}")

def problem_5():
    p = np.array([
        [1/2, 1/2, 0, 0],
        [2/3, 0, 1/3, 0],
        [3/4, 0, 0, 1/4],
        [1, 0, 0, 0]
    ])
    pi = stationary_distribution(p)
    print(f"Shaving Stationary dist: {np.round(pi, 4)}")
    fraction_shaving = pi[0] + pi[1] / 2 + pi[2] / 3 + pi[3] / 4
    print("Fraction shaving:", fraction_shaving)


def clock_return_steps():
    j = 0
    steps = 0
    while True:
        direction = 1 if np.random.uniform(0, 1) > 0.5 else -1
        j = (j + direction) % 12
        steps += 1
        if j == 0:
            return steps



def problem_6():
    steps = [clock_return_steps() for _ in range(100_000)]
    print(f"Average steps of clock simulation: {np.mean(steps)}")


def main():
    problem_5()


if __name__ == '__main__':
    main()