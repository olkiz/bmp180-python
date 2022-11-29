Raspberry Pi Python BMP180 library

### Usage:

```python
from bmp180 import BMP180

bmp = BMP180() # default 1st i2c bus, mode = BMP180_MODE.ULTRA_LOW_POWER
print(bmp.readTemperature(), "\t", bmp.readPressure(), "\t", bmp.calculateAbsoluteAltitude())
```

Or in case of other i2c bus (2 for example)
```python
bmp = BMP180(2)
```

If you want to have other mode:
```python
bmp = BMP180(2, BMP180_MODE.STANDARD)
# or
bmp.setMode(BMP180_MODE.HIGH_RESOLUTION)
```

### Dependencies
Packages:
* smbus2

Also, i2c on device should be enabled.

### Installing:
* `git clone https://github.com/olkiz/bmp180-python.git`
* `cd bmp180-python`
* `pip3 install .`
