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


def problem_5():
    N = 10
    alpha = 0.4
    a = 0.2
    beta = 0.001
    b = 0.001 * np.exp(1)

    ps = [beta * np.exp(alpha * n) for n in range(1, N)]
    qs = [b * np.exp(a * m) for m in range(1, N)]  # m = n - 1
    p = prob_mat(alpha, a, beta, b, N)

    # Eigenvector corresponding to eigenvalue 1.
    stationary_dist = stationary_distribution(p)
    print(f"(stationary dist) eigenvector: {stationary_dist}")


    # Iterative computation of stationary distribution.
    iterative_dist = [1]
    for p_n, q_np1 in zip(ps, qs):
        iterative_dist.append(iterative_dist[-1] * p_n / q_np1)
    iterative_dist = np.array(iterative_dist) / np.sum(iterative_dist)
    print(f"stationary iterative: {np.round(iterative_dist, 6)}")


    # Analytic simplication of stationary distribution
    dist_analytic = np.array([
        (beta * np.exp((alpha - a)/2 * k) / b)**(k-1)
        for k in range(1, N + 1)
    ])
    dist_analytic1 = np.array([
        np.exp((k-1) * (np.log(beta / b) + 0.5 * (alpha - a) * k))
        for k in range(1, N+1)
    ])
    dist_analytic1 /= np.sum(dist_analytic1)
    dist_analytic /= np.sum(dist_analytic)
    print("Difference!!!!!!!!!!!!!!!!!", dist_analytic - dist_analytic1)
    print(f"Analytic: {np.round(dist_analytic, 6)}")

    # Verify that these computations yield the same results
    assert np.all(np.isclose(stationary_dist, iterative_dist))
    assert np.all(np.isclose(stationary_dist, dist_analytic))
    assert np.all(np.isclose(stationary_dist, dist_analytic1))

    # Run simulation.
    x_sim = simulate_chain(p, int(1e5), mu0=stationary_dist)
    x_sim = np.array(x_sim) + 1  # Convert simulation results from 0 to 1-indexed.

    # fig = plt.figure()
    bins = np.arange(0, N + 1) + 0.5
    plt.hist(x_sim, density=True, bins=bins, log=True)
    plt.plot(np.arange(1, N + 1), dist_analytic, 'k-')
    plt.plot(np.arange(1, N + 1), dist_analytic1, 'o--')
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
    for i, cumsum in enumerate(cdf):
        if u < cumsum:
            return pi[i]
    raise ValueError("Uniform sample out of range...;")

def ordered_cdf(mu):
    pi = np.argsort(mu)[::-1]
    cdf = np.cumsum(mu[pi])
    return cdf, pi


def simulate_chain(p, n, mu0=None):
    if mu0 is None:
        # Default to sampling initial state uniformly.
        mu0 = np.full(p.shape[0], 1 / p.shape[0])

    # Pre-compute CDF and permuation for each row in probability
    # matrix so it doesn't need to be recomputed each step.
    cdfs, pis = zip(*[ordered_cdf(mu) for mu in p])
    pis = np.array(pis)
    cdfs = np.array(cdfs)

    xs = [sample_discrete(*ordered_cdf(mu0))]
    u = np.random.uniform(0, 1, n - 1)
    for u_i in u:
        pi, cdf = pis[xs[-1]], cdfs[xs[-1]]
        xs.append(sample_discrete(cdf, pi, u_i))
    return xs
            

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





def main():
    problem_5()



if __name__ == '__main__':
    main()