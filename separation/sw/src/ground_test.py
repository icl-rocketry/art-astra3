import time
import board
import neopixel
from analogio import AnalogIn
from speaker import Speaker

vin = AnalogIn(board.A1)
buzzer = Speaker(Aout = board.MISO)

def get_voltage():
    reading = (vin.value * 3.3) / 65536
    R1 = 220000
    R2 = 120000
    return (reading/R2) * (R1+R2)

led = neopixel.NeoPixel(board.NEOPIXEL, 1)
serpow = board.A3
servo = board.A2

while True:
    led.fill((255, 0, 0))
    time.sleep(0.5)
    led.fill((0, 255, 0))
    # time.sleep(0.5)
    print(get_voltage())
    #buzzer.noise()
    led.fill((0, 0, 255))
    #buzzer.siren(cycles = 1)