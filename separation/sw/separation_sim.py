import random
from src.filter import FilteredPressureSensor, Sensor  # type: ignore
from src.trigger import ApogeeTrigger  # type: ignore

TRIGGER_RANGE = 5000  # 5000 milliseconds is 5 seconds after apogee


def read_file(filename: str = "astra2_data.csv") -> tuple[list[tuple[int, float]], int]:
    raw_data: list[tuple[int, float]] = []
    with open(filename, "r") as file:
        for line in file:
            time_str, pressure_str = line.split("\t")
            raw_data += [(int(time_str), float(pressure_str))]
    # print(f"APOGEE PRESSURE = {min(raw_data, key=lambda x: x[1])[1]}")
    return raw_data, min(raw_data, key=lambda x: x[1])[0]


def peturb_trajectory(trajectory: list[tuple[int, float]], sigma: float = 0, outlier_probability: float = 0) -> list[tuple[int, float]]:
    new_trajectory = []
    for (time, pressure) in trajectory:
        pressure += random.gauss(0, sigma)
        if random.random() < outlier_probability:
            pressure = random.uniform(0, 1 << 31)  # Int max is 1<<31
        new_trajectory += [(time, pressure)]
    return new_trajectory


class FakePressureSensor(Sensor):
    def __init__(self, trajectory: list[tuple[int, float]]):
        self._trajectory = trajectory
        self._index = 0

    def read(self) -> float:
        try:
            pressure = self._trajectory[self._index][1]
            self._index += 1

            return pressure
        except IndexError:
            raise StopIteration

    def get_time(self) -> int:
        return self._trajectory[self._index][0]

class SensorConfig:
    class SensorConfigEntry:
        def __init__(self, sigma: float, outlier_probability: float, buffer_size: int):
            self.sigma = sigma
            self.outlier_probability = outlier_probability
            self.buffer_size = buffer_size

    def __init__(self, name: str, trajectory_file: str, trigger_threshold: int, pressure_threshold: float, sensors: list[SensorConfigEntry]):
        self.name = name
        self.trajectory_file = trajectory_file
        self.trigger_threshold = trigger_threshold
        self.pressure_threshold = pressure_threshold
        self.sensors = sensors

def test_separation(sensor_config: SensorConfig) -> tuple[bool, int]:
    trajectory, apogee_time = read_file(sensor_config.trajectory_file)
    
    sensors = []
    filtered_sensors = []
    for sensor_cfg in sensor_config.sensors:
        sensor = FakePressureSensor(peturb_trajectory(
            trajectory, sigma=sensor_cfg.sigma, outlier_probability=sensor_cfg.outlier_probability))
        
        sensors.append(sensor)
        filtered_sensors.append(FilteredPressureSensor(sensor_cfg.buffer_size, sensor))

    trigger = ApogeeTrigger(filtered_sensors, sensor_config.trigger_threshold, sensor_config.pressure_threshold)

    try:
        while not trigger.canSeparate():
            pass
    except StopIteration:
        print("\u001b[31mNo separation\u001b[0m")
        return False, 0

    now = sensors[0].get_time()
    assert all(map(lambda s: s.get_time() == now, sensors))

    return now - apogee_time < TRIGGER_RANGE and now > apogee_time, now - apogee_time


if __name__ == "__main__":
    PRESSURE_THRESHOLD = 100_000 # Pa
    configs = [
        SensorConfig("air-no-peturbation", "astra2_air.tsv", 5, PRESSURE_THRESHOLD, sensors=[
            SensorConfig.SensorConfigEntry(0, 0, 20),
            SensorConfig.SensorConfigEntry(0, 0, 20),
            SensorConfig.SensorConfigEntry(0, 0, 20),
        ]),
        SensorConfig("full-no-peturbation", "astra2_full.tsv", 5, PRESSURE_THRESHOLD, sensors=[
            SensorConfig.SensorConfigEntry(0, 0, 20),
            SensorConfig.SensorConfigEntry(0, 0, 20),
            SensorConfig.SensorConfigEntry(0, 0, 20),
        ]),
        SensorConfig("air-light-noise", "astra2_air.tsv", 5, PRESSURE_THRESHOLD, sensors=[
            SensorConfig.SensorConfigEntry(20, 0, 20),
            SensorConfig.SensorConfigEntry(20, 0, 20),
            SensorConfig.SensorConfigEntry(20, 0, 20),
        ]),
        SensorConfig("full-light-noise", "astra2_full.tsv", 5, PRESSURE_THRESHOLD, sensors=[
            SensorConfig.SensorConfigEntry(20, 0, 20),
            SensorConfig.SensorConfigEntry(20, 0, 20),
            SensorConfig.SensorConfigEntry(20, 0, 20),
        ]),   
        SensorConfig("air-light-noise+outliers", "astra2_air.tsv", 5, PRESSURE_THRESHOLD, sensors=[
            SensorConfig.SensorConfigEntry(20, 0.1, 20),
            SensorConfig.SensorConfigEntry(20, 0.1, 20),
            SensorConfig.SensorConfigEntry(20, 0.1, 20),
        ]),
        SensorConfig("full-light-noise+outliers", "astra2_full.tsv", 5, PRESSURE_THRESHOLD, sensors=[
            SensorConfig.SensorConfigEntry(20, 0.1, 20),
            SensorConfig.SensorConfigEntry(20, 0.1, 20),
            SensorConfig.SensorConfigEntry(20, 0.1, 20),
        ]),   
    ]
    exitCode = 0
    for (i, config) in enumerate(configs):
        passed, diff = test_separation(config)
        timing = "after" if diff > 0 else "before"
        if not passed:
            print(f"\u001b[31mFAILED test: {config.name :<40} SEPARATED {diff}ms {timing} apogee\u001b[0m")
            exitCode += 1
        else:
            print(f"\u001b[32mPASSED test: {config.name :<40} SEPARATED {diff}ms {timing} apogee\u001b[0m")
            ...
    exit(exitCode)
    