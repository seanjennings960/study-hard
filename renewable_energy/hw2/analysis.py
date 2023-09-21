from pathlib import Path
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt

SAVE_DIR = Path.cwd() / "Images"

WIND_SPEED = [
    2.0, 2.6, 1.0, 1.3,
    1.5, 1.3, 2.9, 4.6,
    6.6, 8.6, 8.0, 9.1,
    9.4, 9.4, 7.9, 6.5,
    7.0, 8.8, 7.54, 4.5,
    2.7, 3.3, 4.8, 5.8
]
MPH_PER_METER_PER_SEC = 2.237  # mph / m/s

WIND_SPEED_MS = [s / MPH_PER_METER_PER_SEC for s in WIND_SPEED]  # m/s
FEET_PER_METER = 3.28
BTU_PER_KWH = 3412
D = 179 / FEET_PER_METER  # m
C_P = 0.35
RHO = 1.225

def wind_power(u, rho, A, c_p):
    return 1/2 * rho * A * u**3 * c_p

def problem_1():
    A = np.pi/4 * D**2
    print('Diameter (m): ', D)
    print('Area m^2', A)
    P = np.round([
        wind_power(u, RHO, A, C_P) for u in WIND_SPEED_MS
    ], 2)
    print("wind speed m/s")
    pprint(WIND_SPEED_MS[:10])
    print("Power(kW)")
    pprint(np.round((P/1000), 2).tolist())
    print("Power at 8m/s")
    print(wind_power(7, RHO, A, C_P))
    print("max wind speed (m/s):", max(WIND_SPEED_MS))
    time = np.arange(24)
    fig = plt.figure()  # noqa
    plt.plot(time, P/1000)
    plt.title("Instantaneous Power vs. Time")
    plt.xlabel("Time (hr)")
    plt.ylabel("Power (kW)")
    plt.grid()
    plt.show()
    # fig.savefig(SAVE_DIR / 'WIND_SPEED.png')
    

def problem_2():
    fuel = 75_444_200 * 1e6  # Btu
    generation = 7_561_850 * 1e3  # kWh
    heat_rate = fuel / generation
    print("Heat rate (Btu):", heat_rate)
    print("Efficiency:", BTU_PER_KWH / heat_rate)


# Problem 3
GENERATION = [
    362, 362, 361, 361, 360, 358, 358, 358, 357,
    357, 357, 357, 357, 356, 356, 356, 356, 356,
    356, 356
]  # MW(h)
FUEL = [
    3328, 3152, 3338, 3164, 3321, 3325, 3258, 3248, 3321,
    3321, 3320, 3319, 3298, 3374, 3366, 3317, 3308, 3307,
    3307, 3306
]  # MMBtu

def problem_3():
    print(len(GENERATION), len(FUEL))
    fig = plt.figure()  # noqa
    plt.plot(FUEL)
    plt.title("Heat Input Curve")
    plt.xlabel("Time (hr)")
    plt.ylabel("Heat input (MMBtu)")
    plt.ylim(0, 4000)
    plt.grid()
    plt.show()
    # fig.savefig(SAVE_DIR / 'heat_input_curve.png')

    heat_rate = [f * 1e6 / (g * 1e3) for (f, g) in zip(FUEL, GENERATION)]
    fig = plt.figure()  # noqa
    plt.plot(heat_rate)
    plt.title("Heat Rate Curve")
    plt.xlabel("Time (hr)")
    plt.ylabel("Heat rate (Btu)")
    plt.ylim(3000, 15_000)
    plt.grid()
    plt.show()
    # fig.savefig(SAVE_DIR / 'heat_rate_curve.png')

    print("Mean efficiency:", BTU_PER_KWH / np.mean(heat_rate))

def problem_4():
    P = 20 
    Q = 15
    pf = np.arctan(Q/P)
    print('power factor:', pf)

    vecs = np.array([
        [0, 20],
        [20, 0],
        [0, -5]
    ])
    labels = ['Inductor', 'Resistor', 'Capacitor']
    tip = np.array([0, 0])
    fig = plt.figure()  # noqa
    for (vec, label) in zip(vecs, labels):
        end = tip + vec
        plt.plot([tip[0], end[0]], [tip[1], end[1]], label=label)
        tip = end
    plt.plot([0, P], [0, Q], label='Total')
    plt.title("Power triangle: by component")
    plt.xlabel("Real Power (W)")
    plt.ylabel("Reactive Power (VAr)")
    plt.legend()
    plt.show()
    fig.savefig(SAVE_DIR / 'power_triangle_component.png')
    
    fig = plt.figure()  # noqa
    plt.plot([0, P], [0, Q], label='Total')
    plt.plot([0, P], [0, 0], label='Real')
    plt.plot([P, P], [0, Q], label='Reactive')
    plt.title("Power triangle: real vs reactive")
    plt.xlabel("Real Power (W)")
    plt.ylabel("Reactive Power (VAr)")
    plt.legend()
    plt.show()
    fig.savefig(SAVE_DIR / 'power_triangle_real.png')



BUSES = [
    4, 5, 6, 7, 8,
    9, 10, 11, 12, 13,
    14, 15
]

REAL_POWERS = [
    60, 100, 80, 90, 40,
    10, 15, 75, 40, 30,
    35, 10
]
REACTIVE_POWERS = [
    10, 30, 15, 20, 5,
    5, 10, 15, 15, 10,
    10, 0
]

def problem_5():
    S = [np.sqrt(p**2 + q**2) for (p, q) in zip(REAL_POWERS, REACTIVE_POWERS)]
    print('Apparent powers')
    pprint(np.round(S, 2).tolist())
    print('Total real power:', np.sum(REAL_POWERS))
    print('Total reactive power:', np.sum(REACTIVE_POWERS))
    i = np.argmax(S)
    print("Maximum load (i, bus, load):", i, BUSES[i], S[i])





if __name__ == '__main__':
    # problem_1()
    # problem_2()
    # problem_3()
    # problem_4()
    problem_5()
