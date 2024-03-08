from bisect import bisect_left
from functools import lru_cache

import numpy as np
import matplotlib.pyplot as plt


def prob_mat(alpha, a, beta, b, N):
    p = np.zeros((N, N), dtype=np.float64)
    for i in range(N):
        # i is 0-index; n is 1-indexed.
        n = i + 1
        if i < N - 1:
            p_n = beta * np.exp(alpha * n)
            p[i, i + 1] = p_n
        else:
            p_n = 0
        if i > 0:
            q_n = b * np.exp(a * i)
            p[i, i - 1] = q_n
        else:
            q_n = 0
        p[i, i] = 1 - p_n - q_n
    return p

def stationary_distribution(p):
    lambdas, vec = np.linalg.eig(p.T)
    eig_1 = np.argwhere(np.isclose(lambdas, 1))
    assert len(eig_1) == 1, "Probability matrix must be irreducible."
    column = eig_1[0, 0]
    stationary_dist = vec[:, column]
    assert np.all(np.isclose(np.imag(stationary_dist), 0)), "Perron frobenius violation"
    stationary_dist /= np.sum(stationary_dist)
    return np.real(stationary_dist)

def problem_6():
    prob_mats = {
        "a": np.array([
            [0, 1, 0],
            [1/2, 0, 1/2],
            [1, 0, 0]
        ]),
        "b": np.array([
            [0, 1, 0, 0],
            [1/2, 0, 1/2, 0],
            [0, 0, 0, 1],
            [1, 0, 0, 0]
        ]),
        "c": np.array([
            [0, 1, 0, 0],
            [0, 0, 1/2, 1/2],
            [0, 0, 0, 1],
            [1, 0, 0, 0]
        ]),
        "d": np.array([
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1/2, 0, 1/2, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 1/2, 0, 0, 0, 1/2],
            [1, 0, 0, 0, 0, 0]
        ])
    }

    dists = {
        name: stationary_distribution(p)
        for name, p in prob_mats.items()
    }
    for name, dist in dists.items():
        print(f"Part {name}: {np.round(dist, 4)}")


def problem_5():
    N = 10
    alpha = 0.4
    a = 0.2
    beta = 0.001
    b = 0.001
    ps = [beta * np.exp(alpha * n) for n in range(1, N)]
    qs = [b * np.exp(a * m) for m in range(1, N)]  # m = n - 1
    p1 = prob_mat(alpha, a, beta, b, N)
    p2 = np.zeros((N, N), dtype=np.float64)
    for i, (p_n, q_n) in enumerate(zip(ps + [0], [0] + qs)):
        if i <  N - 1:
            p2[i, i + 1] = p_n
        if i > 0:
            p2[i, i - 1] = q_n
        p2[i, i] = 1 - p_n - q_n

    assert np.all(np.isclose(p1, p2))

    stationary_dist = stationary_distribution(p1)
    print(f"(stationary dist) eigenvector: {stationary_dist}")

    pis = [1]
    for p_n, q_np1 in zip(ps, qs):
        pis.append(pis[-1] * p_n / q_np1)
    pis = np.array(pis) / np.sum(pis)
    print(f"stationary iterative: {np.round(pis, 6)}")

    dist_analytic = [
        (beta * np.exp((alpha - a)/2 * k) / b)**(k-1)
        for k in range(1, N + 1)
    ]

    dist_analytic /= np.sum(dist_analytic)
    print(f"Analytic: {np.round(dist_analytic, 6)}")

    assert np.all(np.isclose(stationary_dist, pis))
    assert np.all(np.isclose(stationary_dist, dist_analytic))

    mu0 = np.zeros(N, dtype=np.float64)
    mu0[0] = 1
    x_sim = simulate_chain(p1, int(1e5), mu0=stationary_dist)
    bins = np.arange(0, N + 1) + 0.5
    x_sim = np.array(x_sim) + 1
    # fig = plt.figure()
    plt.hist(x_sim, density=True, bins=bins, log=True)
    plt.plot(np.arange(1, N + 1), stationary_dist, 'o-')
    plt.grid(True, "major")
    plt.grid(True, "minor", linestyle="--")
    plt.xlabel("State X in S")
    plt.ylabel("Fraction of time in state X")
    plt.title("Markov Chain Simulation and Theoretical Distributions (10^8 steps)")
    plt.legend(["Theoretical", "Simulated"])
    # fig.savefig("Images/simulation.png")
    plt.show()
    

def sample_discrete(cdf, pi, u=None):
    if u is None:
        u = np.random.uniform(0, 1)
    index = bisect_left(cdf, u)
    return pi[index]

def ordered_cdf(mu):
    pi = np.argsort(mu)[::-1]
    cdf = np.cumsum(mu[pi])
    return cdf, pi


def simulate_chain(p, n, mu0=None):
    if mu0 is None:
        mu0 = np.full(p.shape[0], 1 / p.shape[0])

    cdfs, pis = zip(*[ordered_cdf(mu) for mu in p])
    pis = np.array(pis)
    cdfs = np.array(cdfs)
    # pis = [np.argsort(mu)[::-1] for mu in p]
    # cdfs = [np.cumsum(mu[pi]) for mu, pi in zip(p, pis)]
    xs = [sample_discrete(*ordered_cdf(mu0))]
    print(xs)
    u = np.random.uniform(0, 1, n - 1)
    for u_i in u:
        pi, cdf = pis[xs[-1]], cdfs[xs[-1]]
        xs.append(sample_discrete(cdf, pi, u_i))
    return xs
            





def main():
    problem_6()



if __name__ == '__main__':
    main()