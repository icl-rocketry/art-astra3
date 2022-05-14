#In this file we have a FilteredPressureSensor class which has a variable length buffer and a sensor object.
#Each pressure sensor will have a FilteredPressureSensor object associated with it.
#During flight, the FilteredPressureSensor will take in a sensor reading and output a smoothed pressure value.

class Sensor:
    pressure = 0

class RingBuffer:
    def __init__(self, maxlen):
        self._w = 0
        self._r = 0
        self._data = [0] * maxlen
        self._maxlen = maxlen
        self._len = 0

    def append(self, item):
        if self._w == self._r and self._data[self._w] != 0: #Hack to make sure that this isn't the first write
            self._r += 1
            self._r %= self._maxlen
        self._data[self._w] = item
        self._w += 1
        self._w %= self._maxlen
        self._len += 1

    def __iter__(self):
        i = self._r
        yield self._data[i]
        i += 1
        i %= self._maxlen
        while i != self._w:
            yield self._data[i]
            i += 1
            i %= self._maxlen

    def __len__(self):
        return min(self._len, self._maxlen)

class FilteredPressureSensor:
    def __init__(self, bufferSize: int, sensor: Sensor):
        self._bufferSize = bufferSize
        self._buffer = RingBuffer(bufferSize)
        self._sensor = sensor

    def read(self) -> float:
        self._buffer.append(self._sensor.pressure)
        median = sorted(self._buffer)[len(self._buffer) // 2] #Median filter to remove outliers
        return median