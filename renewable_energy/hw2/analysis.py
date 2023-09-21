from pathlib import Path
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt

SAVE_DIR = Path.cwd() / "images"

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
    fig = plt.figure()
    plt.plot(time, P/1000)
    plt.title("Instantaneous Power vs. Time")
    plt.xlabel("Time (hr)")
    plt.ylabel("Power (kW)")
    plt.grid()
    plt.show()
    # fig.savefig(SAVE_DIR / 'WIND_SPEED.png')
    


if __name__ == '__main__':
    problem_1()
