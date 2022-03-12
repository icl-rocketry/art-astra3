#In this file we have a FilteredPressureSensor class which has a variable length buffer and a sensor object.
#Each pressure sensor will have a FilteredPressureSensor object associated with it.
#During flight, the FilteredPressureSensor will take in a sensor reading and output a smoothed pressure value.

from collections import deque

class FilteredPressureSensor:
    def __init__(self, bufferSize: int, sensor):
        self._bufferSize = bufferSize
        self._buffer = deque(maxlen=bufferSize)
        self._sensor = sensor

    def read() -> float:
        self._buffer.append(self._sensor.read())
        mean = sum(self._buffer) / len(self._buffer)
        return mean