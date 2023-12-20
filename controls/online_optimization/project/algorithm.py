import numpy as np
import dykstra


def proj_halfspace(x, c, b):
    # Project the point x onto the half-space
    # H:={y in Real | c^T y <= b} with c, x in R^n,
    # ||c|| > 0 and b in R.
    d = np.dot(c, x) - b
    if d <= 0:
        return x
    # Normalize c, b ahead of time to speed up.
    return x - d * c / np.dot(c, c)

class _ProjHS:
    def __init__(self, A, b, i):
        self.A_i = A[i]
        self.b_i = b[i]
    
    def __call__(self, x):
        return proj_halfspace(x, self.A_i, self.b_i)


class ConvergenceError(Exception):
    """Error in convergence of projection algorithm."""


def proj_polytope(x, A, b, check_convergence=True, **kwargs):
    assert A.shape[1] == x.shape[0]
    assert A.shape[0] == b.shape[0]
    proj = [
        _ProjHS(A, b, i)
        for i in range(A.shape[0])
    ]
    x_proj = dykstra.project(proj, x, **kwargs)
    if not np.all(A @ x_proj <= b + 1e-1):
        raise ConvergenceError(
            f"Algorithm failed to converge in {kwargs.get('max_iter', 1000)} iterations")
    return x_proj


class MarketESSCost:
    """Implements the cost function for an MPC-based market-optimized ESS."""

    def __init__(self, gamma, delta_t, price):
        self.gamma = gamma
        self.delta_t = delta_t
        self.p = price

    def eval(self, u):
        """
        Return cost of the predicted control, u.
        
        u in R^T, where T is the number of timesteps of prediction.
        """
        return 1/2 * self.gamma * np.linalg.norm(u)**2 - np.dot(self.p, u) * self.delta_t

    def gradient(self, u):
        return self.gamma * u - self.p * self.delta_t



class PGDAlgorithm:
    """Implements the Projected Gradient Descent algorithm for market-optimized ESS."""
    def __init__(self, gamma, E_min, E_max, delta_t, time_horizon, alpha, max_iter=None):
        self.gamma = gamma
        self.alpha = alpha
        self.T = time_horizon
        self.Gamma = np.tril(np.full((self.T, self.T), -delta_t))
        self.delta_t = delta_t
        self.A = np.r_[
            self.Gamma,
            -self.Gamma
        ]
        self.E_min = E_min
        self.E_max = E_max
        if max_iter is not None:
            self.proj_kwargs = {"max_iter": max_iter}
        else:
            self.proj_kwargs = {}
    
    def project(self, x, u):
        b0 = np.full(self.T, self.E_max - x)
        b1 = np.full(self.T, x - self.E_min)
        b = np.r_[
            b0,
            b1
        ]
        A_flipped = np.flipud(self.A)
        b_flipped = np.flip(b)
        return proj_polytope(u, A_flipped, b_flipped, **self.proj_kwargs)

    def algorithmic_map(self, x, u, price, project=True):
        cost_t = MarketESSCost(self.gamma, self.delta_t, price)
        u_next = u - self.alpha * cost_t.gradient(u)
        if not project:
            return u_next
        return self.project(x, u_next)

    def simulate(self, full_prices, x0=None, u0=None, n_steps=None, use_same_price=False):
        if x0 is None:
            x0 = (self.E_max + self.E_min) / 2
        if u0 is None:
            u0 = np.zeros(self.T, dtype=np.float64)

        assert full_prices.ndim == 1, "full_prices must be a vector"
        if use_same_price:
            n_steps = n_steps
        else:
            n_steps = full_prices.shape[0] - self.T
            assert n_steps > 0, "number of price predictions must longer than the time horizon"

        u_hats = [u0]
        x_list = [x0]
        try:
            for t in range(n_steps):
                # print("Step: ", t)
                if use_same_price:
                    price = full_prices
                else:
                    price = full_prices[t:t+self.T]
                x_t = x_list[-1]
                u_hat_t = u_hats[-1]
                u_next = self.algorithmic_map(x_t, u_hat_t, price)
                x_list.append(
                    x_t - self.delta_t * u_next[0]
                )
                # print('difference:', np.linalg.norm(u_next - u_hat_t))
                if np.all(np.isclose(u_next, u_hat_t)):
                    break
                u_hats.append(u_next)
            return x_list, u_hats
        except ConvergenceError:
            print("FAILED TO CONVERGE!!!")
            return x_list, u_hats


def test_proj_halfspace():
    x = np.array([0, 1])
    cs = np.array([
        [-1, 0],
    ])
    bs = [-1, 1, 0]
    results = []
    for (c, b, res) in zip(cs, bs, results):
        assert np.all(proj_halfspace(x, c, b) == res)


def sloppy_triangle(delta_u, u_max, T):
    u = [0]
    i = 0
    while True:
        while u[-1] < u_max:
            u.append(u[-1] + delta_u)
            i += 1
            if i == T-1:
                return np.array(u)
        while u[-1] > -u_max:
            u.append(u[-1] - delta_u)
            i += 1
            if i == T-1:
                return np.array(u)


def check_convergence(u, A, b, expect_fail):
    try:
        proj_polytope(u, A, b, max_iter=int(1e3))
        if expect_fail:
            raise ValueError("Didn't fail when expected")
    except ConvergenceError:
        if not expect_fail:
            raise ValueError("Failed, when expected to pass")


def test_proj_polytope():
    dt = 15/60
    T = 1000
    E_max = 100
    E_min = 10
    x_t = 50
    gamma = np.tril(np.full((T, T), -dt))
    b0 = np.full(T, E_max - x_t)
    b1 = np.full(T, x_t - E_min)
    A = np.r_[
        gamma,
        -gamma
    ]
    b = np.r_[
        b0,
        b1
    ]
    for u_max in range(10, 90, 10):
        print('u_max:', u_max)
        expect_fail = u_max >= 70
        print('expect fail:', expect_fail)
        u = sloppy_triangle(10, u_max, T)
        check_convergence(u, A, b, expect_fail)