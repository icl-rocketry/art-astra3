import time
import struct

class state:
    def __init__(self, sensors):
        self.sensors = sensors

    def run(self):
        raise NotImplementedError()

class diagnostic(state):
    def __init__(self):
        pass

    def run(self):
        #Initialise sensors
        sensors = 3
        return preflight(sensors)        

class preflight(state):
    PRE_FLIGHT_DELAY = 15 * 60

    def run(self):
        time.sleep(self.PRE_FLIGHT_DELAY)
        return flight(self.sensors)

class flight(state):
    RECORDING_TIME = 20*60
    RECORDING_FREQUENCY = 10
    
    def run(self):
        #12 bytes a reading, 10 readings a second 
        # => 120 bytes stored per second
        # => 7200 bytes stored per minute
        # => 432000 bytes stored per hour, so we can just record for as long as we need, since even
        # For the sake of convenience let's just record for 20 minutes

        file = open("recording.bin", "wb")
        try:
            #TODO: fix this
            for _ in range(self.RECORDING_FREQUENCY*self.RECORDING_TIME):
                data = [s.read() for s in self.sensors]

                if should_trigger(data):
                    trigger()
                
                file.write(data)
        except e:
            file.write("ERROR ERROR\n".encode("ascii")) #Should be exactly 12 bytes for convenience
        finally:
            file.close()