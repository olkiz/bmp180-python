from bmp180 import BMP180

bmp = BMP180()
while True:
    print(bmp.readTemperature(), "\t", bmp.readPressure(), "\t", bmp.calculateAbsoluteAltitude())
