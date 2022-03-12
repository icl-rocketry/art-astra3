#In this file we have a Trigger class, which takes in a few FilteredPressureSensors and a separation altitude threshold
#It has a canSeparate method which returns whether or not we can trigger separation.
#We only trigger separation if we're below separation threshold, and we believe that the rocket is going down.

from filter import FilteredPressureSensor

UP = 1
DOWN = 0

class Trigger:
    def __init__(self, sensors: [FilteredPressureSensor], altitudeThreshold: float):
        self._sensors = sensors
        self._thresh = altitudeThreshold #TODO: convert this to a pressure value
        self._old_readings = [0] * len(sensors)

    def canSeparate() -> bool:
        readings = [s.read() for s in self._sensors]

        votes = [int(new > old) for (new, old) in zip((readings, self._old_readings))] 
        winner = int(sum(votes) > 1)

        masked_readings = [value for (vote, value) in zip((votes, readings)) if vote == winner]

        self._old_readings = readings