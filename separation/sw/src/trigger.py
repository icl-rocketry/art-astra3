# In this file we have a Trigger class, which takes in a the number of sensors and a separation altitude threshold
# It has a canSeparate method which returns whether or not we can trigger separation.
# We only trigger separation if we're below separation threshold, and we believe that the rocket is going down.

UP = 0
DOWN = 1


class ApogeeTrigger:
    MOVEMENT_THRESHOLD = 10 #Only count a change if the values are more than 10 Pascals apart

    def __init__(self, n_sensors: int, threshold: int, pressure_threshold: float):
        self._old_readings = [0.0] * n_sensors
        self._threshold = threshold
        self._pressure_threshold = pressure_threshold
        self._down_combo = 0

    def canSeparate(self, readings: list[float]) -> bool:
        if all(abs(new - old) < self.MOVEMENT_THRESHOLD for (new, old) in zip(readings, self._old_readings)):
            return False
        votes = [int(new >= old)
                 for (new, old) in zip(readings, self._old_readings)]
        winner = int(sum(votes) > 1) #This is broken

        if winner == DOWN:
            self._down_combo += 1
        else:
            self._down_combo = 0
        # print(readings[0], self._down_combo, sep=", ")

        self._old_readings = readings
        return self._down_combo >= self._threshold and all(map(lambda x: x < self._pressure_threshold, readings))
