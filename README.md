Raspberry Pi Python BMP180 library

### Usage:

```python
from bmp180 import BMP180

bmp = BMP180()
print(bmp.readTemperature(), "\t", bmp.readPressure(), "\t", bmp.calculateAbsoluteAltitude())
```

### Dependencies
Packages:
* smbus2

Also, i2c on device should be enabled.

### Installing:
* `git clone https://github.com/olkiz/bmp180-python.git`
* `cd bmp180-python`
* `pip3 install .`