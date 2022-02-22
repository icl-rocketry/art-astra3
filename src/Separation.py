from time import sleep
readings = 100

def altidude(pressure):
     multiplier = 44307.69396     
     alt = multiplier * (1 - (pressure/1013.25)**0.190284)
     return alt
     
print(altidude(1000))

accumulator = 0
for i in range(readings):
    get(pressure)
    accumulator += pressure
    sleep(1)

avg_pressure = accumulator/readings

