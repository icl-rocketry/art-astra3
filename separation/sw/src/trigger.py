#In this file we have a Trigger class, which takes in a few FilteredPressureSensors and a separation altitude threshold
#It has a canSeparate method which returns whether or not we can trigger separation.
#We only trigger separation if we're below separation threshold, and we believe that the rocket is going down.

from .filter import FilteredPressureSensor # type: ignore

UP = 0
DOWN = 1

class ApogeeTrigger:
    def __init__(self, sensors: list[FilteredPressureSensor], threshold: int):
        self._sensors = sensors
        self._old_readings = [0] * len(sensors)
        self._threshold = threshold
        self._down_combo = 0
        self._up_combo = 0


    def canSeparate(self) -> bool:
        readings = [s.read() for s in self._sensors]
        if readings == self._old_readings:
            return False

        votes = [int(new >= old) for (new, old) in zip(readings, self._old_readings)] 
        winner = int(sum(votes) > 1)

        if winner == DOWN:
            self._down_combo += 1
            self._up_combo = 0
        else:
            self._up_combo += 1
            self._down_combo = 0
        # print(readings[0], self._up_combo, self._down_combo, sep=", ")

        self._old_readings = readings
        return self._down_combo >= self._threshold