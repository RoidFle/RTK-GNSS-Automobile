import time
import sys

sys.path.append('/home/gunpi5/Project')
from py_qmc5883l import QMC5883L

I2C_BUS = 1
DEVICE_ADDRESS = 0x0D

sensor = QMC5883L(I2C_BUS, DEVICE_ADDRESS)
sensor.calibration = [
    [1.0, 0.0, 0.0],  #x
    [0.0, 1.0, 0.0],  #y
    [0.0, 0.0, 1.0]   #z
]

def degrees_to_heading(degrees):
    heading = ""
    if (degrees > 337) or (degrees >= 0 and degrees <= 22):
        heading = 'N'
    if degrees > 22 and degrees <= 67:
        heading = "NE"
    if degrees > 67 and degrees <= 112:
        heading = "E"
    if degrees > 112 and degrees <= 157:
        heading = "SE"
    if degrees > 157 and degrees <= 202:
        heading = "S"
    if degrees > 202 and degrees <= 247:
        heading = "SW"
    if degrees > 247 and degrees <= 292:
        heading = "W"
    if degrees > 292 and degrees <= 337:
        heading = "NW"
    return heading

while True:
    try:
        data = sensor.get_magnet()
        print(f"Compass X, Y: {data}")     

        #Angle
        bearing = sensor.get_bearing()
        print(f"Heading: {bearing} Degree")

        #Angle to Direction
        direction = degrees_to_heading(bearing)
        print(f"Direction: {direction}")

    except Exception as e:
        print(f"Error reading from QMC5883L: {e}")
    time.sleep(1)




