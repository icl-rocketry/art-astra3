#In this file we have a FilteredPressureSensor class which has a variable length buffer and a sensor object.
#Each pressure sensor will have a FilteredPressureSensor object associated with it.
#During flight, the FilteredPressureSensor will take in a sensor reading and output a smoothed pressure value.

from collections import deque

class Sensor:
    def read(self) -> float:
        raise NotImplementedError("Sensor not implemented")

class FilteredPressureSensor:
    def __init__(self, bufferSize: int, sensor):
        self._bufferSize = bufferSize
        self._buffer = deque(maxlen=bufferSize)
        self._sensor = sensor

    def read(self) -> float:
        self._buffer.append(self._sensor.read())
        median = sorted(self._buffer)[len(self._buffer) // 2] #Median filter to remove outliers
        return median