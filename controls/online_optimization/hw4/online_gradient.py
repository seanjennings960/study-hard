from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from typing import Callable, Union

STATE_DIM = 2
SAVE_DIR = Path("Images")

class ParametrizedLinearCost:
    def __init__(self, A):
        self.A = A
        hessian_eigvals = np.linalg.eigvals(A.T @ A)
        self.L = max(hessian_eigvals)
        self.mu = min(hessian_eigvals)

    def eval(self, x, w):
        """
        Evaluate cost at a series of timesteps.
        """
        # Decorator makes sure input is dim (timesteps, n)
        return np.linalg.norm(self.A @ x - w, axis=0)

    def gradient(self, x, w):
        """
        Evaluate gradient of cost at (x, w).
        """
        return self.A.T @ (self.A @ x - w)


SIGMA_SUP = np.sqrt(2 * (1 - np.cos(1/10)) + 2 * (1 - np.cos(1/100)))

def disturbance(t):
    return np.array([
        5 + np.sin(t / 10),
        2 + np.sin(t / 100)
    ])

def g(x, w, alpha, gradient):
    """Picard iterator for system."""
    return x - alpha * gradient(x, w)

class Problem:
    timesteps: int
    cost: ParametrizedLinearCost
    x0: np.ndarray
    disturbance: Callable[[float], float]
    stepsize: Union[str, float]

    def __init__(self, timesteps, cost, x0, disturbance, stepsize):
        self.timesteps = timesteps
        self.cost = cost
        self.x0 = x0
        self.disturbance = disturbance
        self.stepsize = stepsize

class Solution:

    def __init__(self, x, w, alpha, problem):
        self.x = x
        self.w = w
        self.problem = problem
        self.cost = problem.cost
        self.x_star = np.linalg.inv(self.cost.A) @ w
        self.alpha = alpha
        self.rho = max(abs(1 - self.cost.L * alpha),
                       abs(1 - self.cost.mu * alpha))
        self.error_bound = self.compute_bound()

    def compute_bound(self):
        """Bound as a function of time."""
        rho_to_t = np.array([
            self.rho**t for t in range(self.problem.timesteps)
        ])
        return rho_to_t * np.linalg.norm(self.x[:, 0]) + (
            (1 - rho_to_t) / (1 - self.rho) * SIGMA_SUP
        ) / np.sqrt(self.cost.mu)


def online_gradient_descent(problem):
    
    # Sequence {x_k}
    x = np.zeros((problem.timesteps, STATE_DIM), dtype=float)
    w = np.zeros((problem.timesteps, STATE_DIM), dtype=float)
    x[0] = problem.x0
    cost = problem.cost
    stepsize = problem.stepsize

    if stepsize == 'optimal':
        alpha = 2 / (cost.L + cost.mu)
    elif stepsize == 'divergent':
        DELTA = 0.0001
        alpha = 2 / cost.L + DELTA
    elif stepsize == 'marginal':
        DELTA = -0.01
        alpha = 2 / cost.L + DELTA
    elif isinstance(stepsize, float):
        alpha = stepsize
    else:
        raise NotImplementedError()
    
    for t in range(problem.timesteps - 1):
        w[t] = problem.disturbance(t)
        x[t+1] = g(x[t], w[t], alpha, cost.gradient)
    # Add in disturbance for last timestep because we only predict in loop.
    w[-1] = problem.disturbance(problem.timesteps - 1)
    return Solution(x.T, w.T, alpha, problem)

def autorange(x, delta, n_points):
    """Find plot bounds that are (min(x) - delta, max(x) + delta)"""
    start, end = min(x) - delta, max(x) + delta
    return np.linspace(start, end, n_points)


def plot_cost_heatmap(solution, name):
    n_points = 100
    delta = 1

    x_sol = solution.x
    x_range = autorange(x_sol[0], delta, n_points)
    y_range = autorange(x_sol[1], delta, n_points)


    x = np.stack(np.meshgrid(x_range, y_range))
    x_flat = x.reshape(2, -1)

    rows = 3
    cols = 3
    # timesteps = x_sol.shape[1]
    num_plots = rows * cols
    interval = 10
    fig, plots = plt.subplots(rows, cols)
    plots = plots.flatten()
    # t_indices = np.linspace(0, timesteps-1, rows * cols, dtype=int)
    t_indices = range(0, num_plots * interval, interval)
    for i, t_index in enumerate(t_indices):

        w = np.full(x_flat.shape, solution.w[:, np.newaxis, t_index])
        cost = solution.cost.eval(x_flat, w)

        plots[i].pcolormesh(x[0], x[1], cost.reshape(x[0].shape))
        plots[i].plot(solution.x[0, t_index], solution.x[1, t_index],
                      'o', label='x_t')
        plots[i].plot(solution.x_star[0, t_index], solution.x_star[1, t_index],
                      'o', label='x*_t')
        if i == 2:
            plots[i].legend()
        plots[i].set_xlabel("x0")
        plots[i].set_ylabel("x1")
        plots[i].set_title(f"t={t_index}")
    # plt.suptitle("Cost function heatmap")
    # fig.tight_layout(pad=0)
    plt.subplots_adjust(left=0.1,
                        bottom=0.1, 
                        right=0.9, 
                        top=0.9, 
                        wspace=0.4, 
                        hspace=0.4)
    # plt.show()

    fig.savefig(SAVE_DIR / f"heatmap_{name}.png")


def plot_cost(solution, name):
    x, w = solution.x, solution.w
    x_star, cost = solution.x_star, solution.cost
    c = cost.eval(x, w)

    error = np.linalg.norm(x - x_star, axis=0)
    error_bound = solution.error_bound

    fig, p = plt.subplots(3, 1)
    p[0].plot(c)
    p[0].set_ylabel("Cost -- f_t(x_t)")
    p[0].set_title("f(x) over iteration index")
    p[1].plot(error)
    p[1].plot(error_bound)
    p[1].set_ylabel("Tracking error")
    p[1].set_xlabel("Iteration index -- t")
    p[2].semilogy(error)
    p[2].semilogy(error_bound)
    p[2].set_ylabel("Tracking error")
    p[2].set_xlabel("Iteration index -- t")
    # plt.show()
    print("saving: ", SAVE_DIR / f"error_{name}")
    fig.savefig(SAVE_DIR / f"error_{name}.png")


def main():
    SAVE_DIR.mkdir(exist_ok=True)
    # Input parameters
    timesteps = 300
    x0 = [10, 5]
    stepsize = 'optimal'
    for i, A in enumerate([
        np.array([
                [1, 0.8], 
                [0.7, 1]
            ]),
        np.eye(2),
        np.array([
            [2, 1],
            [0, 1]
        ])
    ]):

        cost = ParametrizedLinearCost(A)
        print("mu:", cost.mu)
        print("L", cost.L)
        print("SIGMA_SUP:", SIGMA_SUP)
        problem = Problem(timesteps, cost, x0, disturbance, stepsize)

        solution = online_gradient_descent(problem)

        plot_name = f"A{i}"
        plot_cost(solution, plot_name)
        plot_cost_heatmap(solution, plot_name)




if __name__ == '__main__':
    main()