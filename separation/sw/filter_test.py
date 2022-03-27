import random
import matplotlib.pyplot as plt

def generate_trajectory(sigma:int=0, outlier_probability: float=0) -> list[tuple[int, float]]:
    raw_data: list[tuple[int, float]] = []
    with open("astra2_data.csv", "r") as file:
        for line in file:
            time_str, pressure_str = line.split("\t")
            raw_data += [(int(time_str), float(pressure_str))]
    
    trajectory = []
    for (time, pressure) in raw_data:
        pressure += random.gauss(0, sigma)
        if random.random() < outlier_probability:
            pressure = random.uniform(0, 1<<31) # Int max is 1<<31
        trajectory += [(time, pressure)]
    return trajectory

def plot(trajectory: list[tuple[int, float]]) -> None:
    x, y = zip(*trajectory)
    plt.plot(x, y)
    plt.show()

plot(generate_trajectory(sigma=100, outlier_probability=0))