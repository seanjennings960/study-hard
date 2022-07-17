import numpy as np
import quaternion as qt
import matplotlib.pyplot as plt

def gen_vector_quaternion():
    a = np.random.random(3)
    return np.quaternion(*(a/np.linalg.norm(a)))

q1 = gen_vector_quaternion()
q2 = gen_vector_quaternion()

q0 = qt.one
omega = np.quaternion(0, 0, 0.1)

def from_angle_axis(v, theta):
    v /= np.linalg.norm(v)
    return qt.one * np.cos(theta/2) + np.quaternion(*v) * np.sin(theta/2)
 
def generate_const_vel_traj(q0, omega, dt=0.01, steps=100):
    t_array = np.zeros(steps)
    q_array = np.full(steps, q0, dtype=np.quaternion)
    for i in range(steps - 1):
        dq = 1/2 * omega * q_array[i]
        t_array[i+1] = i * dt 
        q_array[i+1] = q_array[i] + dq * dt
    return t_array, q_array

def plot_quat(q_array, q_ind1, q_ind2, lim=1, args=None):
    float_array = qt.as_float_array(q_array)
    try:
        if args is not None:
            plt.plot(float_array[:, q_ind1], float_array[:, q_ind2], args)
        else:
            plt.plot(float_array[:, q_ind1], float_array[:, q_ind2])
    except IndexError:
        plt.plot(float_array[q_ind1], float_array[q_ind2], 'x')
    plt.xlim([-lim, lim])
    plt.ylim([-lim, lim])

def plot_quat_time(t_array, q_array):
    plt.plot(t_array, qt.as_float_array(q_array))
    plt.legend(['q0', 'q1', 'q2', 'q3'])

### Constant velocity quaternion trajectory from numerical integration
# t_array, q_array = generate_const_vel_traj(q0, omega, steps=10000)
# plot_quat(q_array, 0, 3)
# plot_quat_time(t_array, q_array)
###

### Plot quaternion tangent vector and exponential map ###
# theta = np.pi2
# q0 = qt.one * np.cos(theta/2) + qt.x * np.sin(theta/2)
# q1 = qt.x
# omega = np.quaternion(0.1, 0, 0)
# # Plot tangent space
# tang_intp = np.arange(-100, 100)
# q_tang = q0 + tang_intp * np.full(tang_intp.shape, omega) * q0
# t_array, q_array = generate_const_vel_traj(q0, omega, steps=10000)
# plot_quat(q_array, 0, 1)
# plot_quat(q_tang, 0, 1, lim=1.5)
# 
# # Plot exponential map points
# t = 5 
# point_tang = q0 + t * omega * q0
# point_map = np.exp(t * omega) * q0
# print('tangent point: ', point_tang)
# print('mapped point: ', point_map)
# plot_quat(point_tang, 0, 1)
# plot_quat(point_map, 0, 1, lim=1.5)
##########################################

q0 = qt.one
theta0 = np.pi/3
theta1 = 7 * np.pi/4
axis = np.array([1., 0, 0])
q0 = from_angle_axis(axis, theta0)
q1 = qt.one * np.cos(theta1/2) + qt.x * np.sin(theta1/2)
q2 = from_angle_axis(axis, theta1)

print(q1)
print(q2)
# Rotation from q0 to q1
q_rot = q1 * q0.conj()
# Logarithmic map to tangent space
omega = np.log(q_rot)
ts = np.arange(0, 1, 0.1)
qs = np.exp(omega * ts) * q0

plot_quat(qs, 0, 1, args='x') 

plt.show()

