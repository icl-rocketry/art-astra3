import pwmio
import board
import time
from random import randint

class Speaker: 
    def __init__(self, Aout = board.MISO):
        # speaker defaults as off
        self.speaker = pwmio.PWMOut(Aout, duty_cycle = 0, variable_frequency = True)

    def _playtone(self, frequency):
        self.speaker.frequency = frequency

    def noise(self):
        # generate white noise
        # better for localisation than pure tones
        self.speaker.duty_cycle = 65535 // 2
        minf = 500
        maxf = 6000
        for _ in range(5000):
            self._playtone(randint(minf, maxf))
            time.sleep(0.001)
        # self.shutup()

    def _sweep(self, startf = 300, endf = 8100, step = 10, delay = 0.0025):
        for f in range(startf, endf, step):
            self._playtone(f)
            time.sleep(delay)

    def siren(self, cycles = 3):
        self.speaker.duty_cycle = 65535 // 2
        # 3x sweep up and down
        for _ in range(cycles):
            self._sweep()
            self._sweep(startf = 8100, endf = 300, step = -10)

    def shutup(self):
        #self._playtone(0)
        self.speaker.duty_cycle = 0
    
    def beep(self, frequency = 4000):
        self.speaker.duty_cycle = 65535 // 2
        self._playtone(frequency)
        time.sleep(0.2)
        self.speaker.duty_cycle = 0
