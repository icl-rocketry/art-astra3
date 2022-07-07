import random
from src.fps import FilteredPressureSensor, Sensor  # type: ignore
from src.trigger import ApogeeTrigger  # type: ignore
import sys
from tqdm import tqdm
from functools import cache

TRIGGER_RANGE = 5000  # 5000 milliseconds is 5 seconds after apogee

@cache
def read_file(filename: str = "astra2_data.csv") -> tuple[list[tuple[int, float]], int]:
    raw_data: list[tuple[int, float]] = []
    with open("test_data/"+filename, "r") as file:
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

    @property
    def pressure(self) -> float:
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

    trigger = ApogeeTrigger(len(filtered_sensors), sensor_config.trigger_threshold, sensor_config.pressure_threshold)

    try:
        readings = [sensor.read() for sensor in filtered_sensors]
        while not trigger.canSeparate(readings):
            readings = [sensor.read() for sensor in filtered_sensors]
    except StopIteration:
        print("\u001b[31mNo separation\u001b[0m")
        return False, 0

    now = sensors[0].get_time()
    assert all(map(lambda s: s.get_time() == now, sensors))

    return now - apogee_time < TRIGGER_RANGE and now >= apogee_time, now - apogee_time


if __name__ == "__main__":
    PRESSURE_THRESHOLD_ASTRA2 = 100_000 # Pa
    PRESSURE_THRESHOLD_ASTRA3 = 99_000 # Pa

    n_reps = int(sys.argv[1])
    MEDIAN_FILTER_SIZE = 15

    configs = [
        SensorConfig("air-no-peturbation", "astra2_air.tsv", 5, PRESSURE_THRESHOLD_ASTRA2, sensors=[
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("full-no-peturbation", "astra2_full.tsv", 5, PRESSURE_THRESHOLD_ASTRA2, sensors=[
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("vac-no-peturbation", "dps310.tsv", 5, PRESSURE_THRESHOLD_ASTRA3, sensors=[
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("vac-no-peturbation-1", "dps310_1.tsv", 5, PRESSURE_THRESHOLD_ASTRA3, sensors=[
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(0, 0, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("air-light-noise", "astra2_air.tsv", 5, PRESSURE_THRESHOLD_ASTRA2, sensors=[
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("full-light-noise", "astra2_full.tsv", 5, PRESSURE_THRESHOLD_ASTRA2, sensors=[
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("vac-light-noise", "dps310.tsv", 5, PRESSURE_THRESHOLD_ASTRA3, sensors=[
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("vac-light-noise-1", "dps310_1.tsv", 5, PRESSURE_THRESHOLD_ASTRA3, sensors=[
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("air-light-noise+outliers", "astra2_air.tsv", 5, PRESSURE_THRESHOLD_ASTRA2, sensors=[
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("full-light-noise+outliers", "astra2_full.tsv", 5, PRESSURE_THRESHOLD_ASTRA2, sensors=[
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("vac-light-noise+outliers", "dps310.tsv", 5, PRESSURE_THRESHOLD_ASTRA3, sensors=[
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
        ]),
        SensorConfig("vac-light-noise+outliers-1", "dps310_1.tsv", 5, PRESSURE_THRESHOLD_ASTRA3, sensors=[
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
            SensorConfig.SensorConfigEntry(20, 0.1, MEDIAN_FILTER_SIZE),
        ]),
    ]
    exitCode = 0
    for (i, config) in enumerate(configs):
        n_passed, after_diff_avg, before_diff_avg = 0, 0, 0
        n_before, n_after = 0, 0
        for _ in tqdm(range(n_reps)):
            passed, diff = test_separation(config)
            n_passed += passed
            if diff < 0:
                before_diff_avg -= diff
                n_before += 1
            else:
                after_diff_avg += diff
                n_after += 1
        
        print(f"""
                {config.name} passed {n_passed} times
                Average premature separation time: {before_diff_avg / n_before if n_before != 0 else 0}
                Average separation delay: {after_diff_avg / n_after}
            """.replace("\t", ""))
    