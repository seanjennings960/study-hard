import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

NE_LOAD_DATA = [
    14986.78,
    14433.29,
    14152.24,
    13846.08,
    13872.55,
    14420.1,
    15115.68,
    15847.59,
    16618.39,
    17459.65,
    17972.45,
    18582.74,
    19047.27,
    19703.17,
    20361.14,
    20941.57,
    21359.46,
    21248.77,
    20582.9,
    19662.8,
    18848.15,
    17434.29,
    15777.38,
    14207.33
]


SIMPLE_LOAD_DATA = (
    [0, 4, 6, 8, 12, 14, 16, 18, 20, 22, 24],
    [50, 50, 75, 150, 150, 175, 175, 200, 200, 0, 0]
)

SAVE_DIR = Path("/home/sean/code/study-hard/renewable_energy/hw1/")

def plot_ne_load_data():
    t = np.arange(1, 25)
    load_data_gw = [load / 1000 for load in NE_LOAD_DATA]
    fig = plt.figure()
    plt.plot(t, load_data_gw)
    plt.title("New England Load Data for August 25th, 2020")
    plt.xlabel("Time (hr)")
    plt.ylabel("Load (GWh)")
    plt.grid(True, which="major")
    plt.grid(True, which="minor", linestyle="--")
    plt.minorticks_on()
    peak_load = np.max(load_data_gw)
    av_load = np.mean(load_data_gw)
    print(f"Total energy: {np.sum(load_data_gw)} GWh")
    print(f"Peak load: {peak_load} GW")
    print(f"Average load: {av_load} GW")
    # plt.show()
    # fig.savefig(SAVE_DIR / "ne_load_plot.png")

def trapezoid_area(t0, t1, p0, p1):
    return (p0 + p1) / 2 * (t1 - t0)

def total_energy():
    t_array, p_array = SIMPLE_LOAD_DATA
    energy_per_interval = [
        trapezoid_area(t0, t1, p0, p1)
        for (t0, t1, p0, p1) in zip(
            t_array[:-1], t_array[1:],
            p_array[:-1], p_array[1:]
        )
    ]
    print("Energy per interval:", energy_per_interval)
    return np.sum(energy_per_interval)

def average_load():
    energy = total_energy()
    l_av = energy/24
    l_peak = max(SIMPLE_LOAD_DATA[1])
    print(f"Total energy {energy} MWh")
    print(f"Average load: {l_av} MW")
    print(f"Load factor = {l_av} / {l_peak} =  {100*l_av/l_peak}%")

####################################################
# Problem 4
####################################################

E_by_hour = [
    410, 400, 400, 415, 430, 450, 480, 490, 500, 500, 500, 500, 500, 500, 500,
    500, 500, 500, 500, 500, 500, 500, 475, 450
]

def daily_capacity_factor():
    total_e = np.sum(E_by_hour)
    average_p = total_e / 23
    capacity = 500
    print(f"total energy: {total_e} MWh")
    print(f"Average generation power: {average_p}")
    print(f"Capacity factor: {100 * average_p / capacity} %")

def wind_power():
    rho = 1.225
    D = 50
    A = np.pi/4*D**2
    U = 43.2/3.6
    Cp = 0.4
    P = 1/2 * rho * A * U**3 * Cp
    print(f"Area: {A}")
    print(f"Wind speed (m/s): {U}")
    print(f"Total wind power: {P}")


if __name__ == '__main__':
    # plot_ne_load_data()
    # average_load()
    # daily_capacity_factor()
    wind_power()
