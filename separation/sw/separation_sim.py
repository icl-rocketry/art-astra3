import random
import matplotlib.pyplot as plt  # type: ignore
from src.filter import FilteredPressureSensor, Sensor  # type: ignore
from src.trigger import Trigger  # type: ignore

TRIGGER_RANGE = 5000  # 5000 milliseconds is 5 seconds after apogee


def read_file(filename: str = "astra2_data.csv") -> tuple[list[tuple[int, float]], int]:
    raw_data: list[tuple[int, float]] = []
    with open(filename, "r") as file:
        for line in file:
            time_str, pressure_str = line.split("\t")
            raw_data += [(int(time_str), float(pressure_str))]
    return raw_data, min(raw_data, key=lambda x: x[1])[0]


def peturb_trajectory(trajectory: list[tuple[int, float]], sigma: float = 0, outlier_probability: float = 0) -> list[tuple[int, float]]:
    new_trajectory = []
    for (time, pressure) in trajectory:
        pressure += random.gauss(0, sigma)
        if random.random() < outlier_probability:
            pressure = random.uniform(0, 1 << 31)  # Int max is 1<<31
        new_trajectory += [(time, pressure)]
    return new_trajectory


def plot(trajectory: list[tuple[int, float]]) -> None:
    x, y = zip(*trajectory)
    plt.plot(x, y)
    plt.show()


class FakePressureSensor(Sensor):
    def __init__(self, trajectory: list[tuple[int, float]]):
        self._trajectory = trajectory
        self._index = 0

    def read(self) -> float:
        pressure = self._trajectory[self._index][1]
        self._index += 1

        return pressure

    def get_time(self) -> int:
        return self._trajectory[self._index][0]

class SensorConfig:
    class SensorConfigEntry:
        def __init__(self, sigma: float, outlier_probability: float, buffer_size: int):
            self.sigma = sigma
            self.outlier_probability = outlier_probability
            self.buffer_size = buffer_size

    def __init__(self, trajectory_file: str, separation_threshold: float, sensors: list[SensorConfig.SensorConfigEntry]):
        self.trajectory_file = trajectory_file
        self.separation_threshold = separation_threshold
        self.sensors = sensors

def test_separation(sensor_config: SensorConfig) -> bool:
    trajectory, apogee_time = read_file(sensor_config.trajectory_file)
    
    sensors = []
    filtered_sensors = []
    for sensor_cfg in sensor_config.sensors:
        sensor = FakePressureSensor(peturb_trajectory(
            trajectory, sigma=sensor_cfg.sigma, outlier_probability=sensor_cfg.outlier_probability))
        
        sensors.append(sensor)
        filtered_sensors.append(FilteredPressureSensor(sensor_cfg.buffer_size, sensor))

    trigger = Trigger(filtered_sensors, sensor_config.separation_threshold)

    while not trigger.canSeparate():
        pass

    now = sensors[0].get_time()
    assert all(map(lambda s: s.get_time() == now, sensors))

    return now - apogee_time < TRIGGER_RANGE and now > apogee_time
