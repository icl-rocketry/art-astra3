def altidude(pressure):
     multiplier = 44307.69396     
     alt = multiplier * (1 - (pressure/1013.25)**0.190284)

     return alt
     
print(altidude(1000))

