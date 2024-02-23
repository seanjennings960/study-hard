import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


def phase_space(dynamics, x1_range, x2_range, x0s=None, t_span=None):

    x_1, x_2 = np.meshgrid(x1_range, x2_range)
    x_dot = dynamics(None, np.dstack([x_1, x_2]))
    x_1_dot = x_dot[..., 0]
    x_2_dot = x_dot[..., 1]
    

    fig = plt.figure()
    mag = np.linalg.norm(np.dstack([x_1_dot, x_2_dot]), axis=-1)
    plt.quiver(x_1, x_2, x_1_dot, x_2_dot, mag, angles='xy', minshaft=0, minlength=1)

    if x0s is not None:
        assert t_span is not None
        x_solutions = [solve_ivp(dynamics, t_span, x0, atol=1e-8, rtol=1e-10) for x0 in x0s]
        for i, traj in enumerate(x_solutions):
            plt.plot(traj.y[0, 0], traj.y[1,0], marker='o', linestyle='', color=f"C{i}", label=f"x0 = {x0s[i]}")
            plt.plot(traj.y[0], traj.y[1], color=f"C{i}", label=f"Trajectory {i}")
        plt.legend()
    return fig

def concat(arrs):
    # Concatenate arrays of equal dimension along last axis
    return np.concatenate([
        arr[..., np.newaxis] for arr in arrs
    ], axis=-1)


def problem1():
    mu0 = 1

    def dynamics(t, x, mu):
        x1_dot = - mu * x[..., 1]
        x2_dot = mu * x[..., 0]
        return concat([x1_dot, x2_dot])

    def sensitivity(t, x, mu):
        dx1dmu = x[..., 2]
        dx2dmu = x[..., 3]
        return concat([
            -x[..., 1] - mu * dx2dmu,
            x[..., 0] + mu * dx1dmu
        ])
    
    def full_dyn(t, x, mu):
        d = dynamics(t, x, mu)
        s = sensitivity(t, x, mu)
        return np.concatenate([
            d, s
        ], axis=-1)


    t_span = [0, 20]
    x0 = np.array([1, 0, 0, 0])
    solution = solve_ivp(full_dyn, t_span, x0, atol=1e-8, rtol=1e-10, args=(mu0,))
    dx1dmu = solution.y[2]
    dx2dmu = solution.y[3]
    fig = plt.figure()
    plt.plot(solution.t, dx1dmu, label='dx1/dmu')
    plt.plot(solution.t, dx2dmu, label='dx2/dmu')
    plt.title("Sensitivity function over time")
    plt.xlabel("Time (s)")
    plt.ylabel("S(t)")
    plt.legend()
    fig.savefig("Images/sensitivity.png")
    plt.show()

def problem3():
    a = 1
    def dynamics_linear(t, x):
        return x @ np.array([
            [0, -1],
            [1, 0]
        ]).T

    def dynamics_nonlinear(t, x):
        x1 = x[..., 0]
        x2 = x[..., 1]
        r_2 = (x1**2 + x2**2)
        return concat([
            -x2 + a * x1 * r_2,
            x1 + a * x2 * r_2
        ])

    x_range = np.linspace(-5, 5, 20)
    x_range_zoom = np.linspace(-0.1, 0.1, 20)
    for dynamics, title, x_range in [
        (dynamics_linear, "Linearized Dynamics", x_range),
        (dynamics_nonlinear, "Nonlinear Dynamics", x_range),
        (dynamics_nonlinear, "Nonlinear Dynamics (zoomed)", x_range_zoom),
    ]:
        fig = phase_space(dynamics, x_range, x_range)
        plt.title(title)
        plt.xlabel("x1")
        plt.ylabel("x2")
        fig.savefig(f"Images/{title.replace(' ', '_')}.png")
        plt.show()

    


def main():
    problem3()


if __name__ == '__main__':
    main() 
    

    