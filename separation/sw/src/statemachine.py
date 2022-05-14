import time
import board
from busio import I2C
from fps import FilteredPressureSensor, Sensor
from adafruit_dps310.advanced import DPS310_Advanced as DPS310
from adafruit_dps310.advanced import Rate, Mode, SampleCount
import adafruit_mpl3115a2
from trigger import ApogeeTrigger
import struct
import neopixel

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1) #type: ignore
pixel.brightness = 0.3

class state:
    colour = (0, 0, 0)
    def __init__(self, sensors):
        self.sensors = sensors

    def _run(self) -> state | None:
        raise NotImplementedError()
    
    def run(self) -> state | None:
        pixel.fill(self.colour)
        try:
            return self._run()
        except Exception as e:
            with open("errors.log", "w") as file:
                file.write(str(e))
            pixel.fill((255, 0, 0))
            while True:
                print(str(e))

class dummy_mpl:
    pressure = 4.2

class diagnostic(state):
    colour = (255, 255, 255)

    def __init__(self):
        pass

    def _run(self) -> state:
        #Initialise sensors
        i2c = I2C(sda=board.SDA1, scl=board.SCL1) #type: ignore
        dps1 = DPS310(i2c)
        # dps2 = DPS310(i2c, address=0x76) #For the grounded one
        dps2 = dummy_mpl()

        for dps in [dps1]:
            dps.reset()
            dps.pressure_oversample_count = SampleCount.COUNT_2 #type: ignore
            dps.pressure_rate = Rate.RATE_16_HZ #type: ignore
            dps.temperature_oversample_count = SampleCount.COUNT_16 #type: ignore
            dps.temperature_rate = Rate.RATE_16_HZ #type: ignore
            dps.mode = Mode.CONT_PRESTEMP #type: ignore

            dps.initialize()
            dps.wait_pressure_ready()
            dps.wait_temperature_ready()

        # mpl = adafruit_mpl3115a2.MPL3115A2(i2c)
        mpl = dummy_mpl()
        print("DONE")
        return preflight([dps1, dps2, mpl])

class preflight(state):
    colour = (0, 0, 255)
    PRE_FLIGHT_DELAY = 15 * 60

    def _run(self) -> state:
        time.sleep(self.PRE_FLIGHT_DELAY)
        return flight(self.sensors)

class flight(state):
    colour = (0, 255, 0)
    RECORDING_TIME = 15 * 60 #Record for 15 minutes why not?
    RECORDING_FREQUENCY = 10
    DELAY = 1 / RECORDING_FREQUENCY
    
    def __init__(self, sensors: list[Sensor]):
        self.sensors = [FilteredPressureSensor(20, sensor) for sensor in sensors]

    def _run(self) -> state:
        trigger = ApogeeTrigger(3, 5, 99_000)

        #20 bytes a reading, 10 readings a second 
        # => 200 bytes stored per second
        # => 12000 bytes stored per minute
        # => 660000 bytes stored per hour, so we can just record for as long as we need, since even
        # For the sake of convenience let's just record for 20 minutes

        buffer = bytearray(20)
        file = open("recording.bin", "wb")
        recording_counter = self.RECORDING_FREQUENCY*self.RECORDING_TIME
        multipliers = [100, 100, 1] #Used to ensure each sensor has the same units
        try:
            while True:
                start = time.monotonic_ns() // 1000
                data = [m*s.read() for (s, m) in zip(self.sensors, multipliers)]
                end = time.monotonic_ns() // 1000
                if trigger.canSeparate(data):
                    file.write("Triggered".encode("ascii"))
                    # trigger() #TODO Add this
                    break

                if recording_counter > 0:
                    struct.pack_into("i", buffer, 0, start)
                    for (i, val) in enumerate(data):
                        struct.pack_into("f", buffer, (i+1)*4, val)

                    struct.pack_into("i", buffer, 16, end)
                    file.write(buffer)
                    recording_counter -= 1
                time.sleep(self.DELAY)
        except Exception as e:
            file.write("ERRORERRORERRORERROR".encode("ascii")) #Should be exactly 20 bytes for convenience
        finally:
            file.close()
        return postflight()

class postflight(state):
    colour = (0, 255, 255)

    def __init__(self):
        pass

    def _run(self) -> None:
        while input() != "stop":
            time.sleep(1)