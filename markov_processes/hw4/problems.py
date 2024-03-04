import numpy as np
import matplotlib.pyplot as plt
from bisect import bisect


# One away
# 0: (0, 0.5) inf
# 1: (0.5, 0.7) 0
# 2: (0.7, 0.85) 1
# 3: (0.85, 1) -1
CLOSE_CDF = [0.5, 0.7, 0.85]
CLOSE_NEXT_STATE = {
    0: np.inf, 1: 0, 2: 1, 3: -1
}
def close_next_state():
    u = np.random.uniform(0, 1)
    index = bisect(CLOSE_CDF, u)
    return CLOSE_NEXT_STATE[index]


# More than one away (assume positive...)
# 0: (0, 0.4) (x - 1)
# 1: (0.4, 0.7) (x)
# 2: (0.7, 1) (x - 2)
FAR_CDF = [0.4, 0.7]

def far_next_state(x):
    if x <= 1:
        raise ValueError("Expected x > 1")
    u = np.random.uniform(0, 1)
    index = bisect(FAR_CDF, u)
    if index == 0:
        return x - 1
    elif index == 1:
        return x
    elif index == 2:
        return x - 2
    else:
        raise ValueError


def spider_sim(x0):
    xs = [x0]
    while True:
        last = xs[-1]
        if last == 0 or np.isinf(last):
            return np.array(xs)
        elif last == 1 or last == -1:
            xs.append(close_next_state())
        else:
            xs.append(far_next_state(last))


def problem_8():
    # Run simulations
    n = 10000
    sims = [spider_sim(2) for _ in range(n)]

    # Probability of escaping
    ends = np.array([sim[-1] for sim in sims])
    prob_escape = np.sum(np.isinf(ends)) / n
    print(f"Probability of escape: {prob_escape:.3f}")
    print(f"Analytic: {20/49:.3f}")

    # Expected number of steps in "game"
    num_steps = [len(sim) - 1 for sim in sims]
    exp_steps = np.mean(num_steps)
    print(f"Expected steps: {exp_steps:.3f}")
    print(f"Analytic: {110/49:.3f}")

    # Number of steps in danger
    in_danger_steps = [
        np.sum(np.logical_or(
            sim == 1,
            sim == -1
        )) for sim in sims
    ]
    exp_danger_steps = np.mean(in_danger_steps)
    print(f"Expected in danger: {exp_danger_steps:3f}")
    print(f"Analytic: {40/49:3f}")
    # plt.figure()
    # for sim in sims[:1000]:
    #     sim_copy = sim.copy()
    #     sim_copy[np.isinf(sim_copy)] = 10
    #     plt.plot(sim_copy)
    # plt.xlabel("Steps")
    # plt.ylabel("Distance")
    # plt.show()
    plt.hist(num_steps, density=True)
    plt.show()





def main():
    problem_8()

if __name__ == '__main__':
    main()