import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


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

def problem4():
    a = 2/3
    b = 4/3
    c = d = 1

    x1_range = np.linspace(0, 3, 20)
    x2_range = np.linspace(0, 2, 20)

    def dynamics(t, x):
        # (..., 2)
        x1_dot = (a - b * x[..., 1]) * x[..., 0]
        x2_dot = (c * x[..., 0] - d) * x[..., 1]
        return np.concatenate([x1_dot[..., np.newaxis], x2_dot[..., np.newaxis]], axis=-1)

    x0s = np.array([
        [1, 1],
        [1.2, 0.5],
        [0.25, 1.2]
    ])
    t_span = [0, 20]

    fig = phase_space(dynamics, x1_range, x2_range, x0s, t_span)
    plt.title("Predator/prey interactions")
    plt.xlabel("x1")
    plt.ylabel("x2")
    fig.savefig("Images/pred-prey.png")


    plt.show()


def problem5():

    # def dynamics(t, x_full):
    #     # x of shape (..., 2)
    #     x = x_full[..., 0]
    #     y = x_full[..., 1]

    #     r = np.sqrt(x ** 2 + y**2)
    #     theta = np.arctan2(y, x)

    #     r_dot = r * (1 - r ** 2) + 3 * np.sin(theta)
    #     theta_dot = -1

    #     x_dot = r_dot * np.cos(theta) - r * np.sin(theta) * theta_dot
    #     y_dot = r_dot * np.sin(theta) + r * np.cos(theta) * theta_dot
    #     return np.concatenate([x_dot[..., np.newaxis], y_dot[..., np.newaxis]], axis=-1)
    def dynamics(t, x_full):
        # x of shape (..., 2)
        x = x_full[..., 0]
        y = x_full[..., 1]

        r = np.sqrt(x ** 2 + y**2)
        theta = np.arctan2(y, x)

        # x = -r * np.cos(theta)
        # y = -r * np.sin(theta)

        r_dot = r * (1 - r ** 2) + 1/3 * np.sin(theta)
        theta_dot = -1

        x_dot = r_dot * np.cos(theta) - r * np.sin(theta) * theta_dot
        y_dot = r_dot * np.sin(theta) + r * np.cos(theta) * theta_dot
        return np.concatenate([x_dot[..., np.newaxis], y_dot[..., np.newaxis]], axis=-1)

    x1_range = 0.1* np.linspace(-2, 2, 31)
    x2_range = 0.1* np.linspace(-2, 2, 31)

    x0s = np.array([
        [1, 1],
        [1.2, 0.5],
        [0.25, 1.2],
        [0, -2],
        [0, -0.1],
        [2, 2],
        [-2, -2]
    ])
    t_span = [0, 20]
    phase_space(dynamics, x1_range, x2_range, x0s=x0s, t_span=t_span)
    plt.show()

    







def main():
    problem4()


if __name__ == '__main__':
    main()