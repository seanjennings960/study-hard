import numpy as np
import quaternion as qt
import matplotlib.pyplot as plt
import pdb

q0 = qt.one
num_rotations = 20
theta = 2*np.pi/num_rotations

q_rot = np.cos(theta/2) * qt.one + np.sin(theta/2) * qt.x

print('Rotating by quaternion: {}'.format(q_rot))
print('Norm is: {}'.format(q_rot.norm()))

q_array = np.full((num_rotations + 1,), qt.one)
q_array[0] = q0
for i in range(num_rotations):
    q_array[i + 1] = q_rot * q_array[i] 

# Plot real and x components
q_float_array = qt.as_float_array(q_array)
norms = np.zeros(q_array.shape)
for i, quat in enumerate(q_array):
    norms[i] = quat.norm()
    print(quat.norm())

def set_axes_circle():
    plt.xlim([-1, 1])
    plt.ylim([-1, 1])

plt.figure()
plt.plot(q_float_array[:, 0], q_float_array[:, 1])
set_axes_circle()
plt.figure()
plt.plot(norms)
plt.title('Norms')
plt.show()

