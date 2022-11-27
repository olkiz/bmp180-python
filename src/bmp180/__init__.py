import smbus2 as smbus
from enum import Enum
import time

# BMP180 i2c adress:
BMP180_I2CADDR = 0x77

class BMP180_REGISTER(Enum):
    # Calibration registers:
    AC1 = 0xAA
    AC2 = 0xAC
    AC3 = 0xAE
    AC4 = 0xB0
    AC5 = 0xB2
    AC6 = 0xB4
    B1 = 0xB6
    B2 = 0xB8
    MB = 0xBA
    MC = 0xBC
    MD = 0xBE

    # Other registers:
    CONTROL = 0xF4
    DATA = 0xF6

class BMP180_MODE(Enum):
    ULTRA_LOW_POWER = 0
    STANDARD = 1
    HIGH_RESOLUTION = 2
    ULTRA_HIGH_RESOLUTION = 3

class BMP180_COMMANDS(Enum):
    READ_TEMPERATURE = 0x2E
    READ_PRESSURE = 0x34

class BMP180_Calibration:
    ac1 = None
    ac2 = None
    ac3 = None
    ac4 = None
    ac5 = None
    ac6 = None
    b1 = None
    b2 = None
    mb = None
    mc = None
    md = None

    def __init__(self, ac1, ac2, ac3, ac4, ac5, ac6, b1, b2, mb, mc, md):
        self.ac1 = ac1
        self.ac2 = ac2
        self.ac3 = ac3
        self.ac4 = ac4
        self.ac5 = ac5
        self.ac6 = ac6
        self.b1 = b1
        self.b2 = b2
        self.mb = mb
        self.mc = mc
        self.md = md

class BMP180:
    _i2cBus = None
    _calibration = None
    _mode = None

    def __init__(self, i2cBus=1, mode: BMP180_MODE = BMP180_MODE.ULTRA_LOW_POWER):
        self._i2cBus = smbus.SMBus(i2cBus)
        self._calibration = self._readCalibration()
        self._mode = mode

    def setMode(self, mode: BMP180_MODE):
        self._mode = mode

    def readTemperature(self):
            ut = self._readRawTemp()
            x1 = (ut - self._calibration.ac6) * self._calibration.ac5 >> 15
            x2 = (self._calibration.mc << 11) // (x1 + self._calibration.md)
            b5 = x1 + x2
            return ((b5 + 8) >> 4) / 10.0

    def readPressure(self):
            ut = self._readRawTemp()
            up = self._readRawPressure()
            x1 = (ut - self._calibration.ac6) * self._calibration.ac5 >> 15
            x2 = (self._calibration.mc << 11) // (x1 + self._calibration.md)
            b5 = x1 + x2
            b6 = b5 - 4000
            b62 = b6 ** 2 >> 12
            x1 = (self._calibration.b2 * b62) >> 11
            x2 = self._calibration.ac2 * b6 >> 11
            x3 = x1 + x2
            b3 = ((int(abs(self._calibration.ac1 * 4 + x3)) << self._mode.value ) + 2) >> 2
            x1 = self._calibration.ac3 * b6 >> 13
            x2 = self._calibration.b1 * b62 >> 16
            x3 = ((x1 + x2) + 2) >> 2
            b4 = self._calibration.ac4 * (x3 + 32768) >> 15
            b7 = (up - b3) * (50000 >> self._mode.value)

            #check this
            p = 0
            if b7 < 0x80000000:
                p = b7 * 2 // b4
            else:
                p = b7 // b4 * 2

            x1 = p**2 >> 16
            x1 = (x1 * 3038) >> 16
            x2 = (-7357 * p) >> 16
            return p + ((x1 + x2 + 3791) >> 4)

    def calculateAbsoluteAltitude(self):
        return 44330 * ( 1 - (self.readPressure() / 101325)**(1/5.255))

    def _readCalibration(self) -> BMP180_Calibration:
        ac1 = self._read16BitInt(BMP180_REGISTER.AC1)
        ac2 = self._read16BitInt(BMP180_REGISTER.AC2)
        ac3 = self._read16BitInt(BMP180_REGISTER.AC3)
        ac4 = self._readU16BitInt(BMP180_REGISTER.AC4)
        ac5 = self._readU16BitInt(BMP180_REGISTER.AC5)
        ac6 = self._readU16BitInt(BMP180_REGISTER.AC6)
        b1 = self._read16BitInt(BMP180_REGISTER.B1)
        b2 = self._read16BitInt(BMP180_REGISTER.B2)
        mb = self._read16BitInt(BMP180_REGISTER.MB)
        mc = self._read16BitInt(BMP180_REGISTER.MC)
        md = self._read16BitInt(BMP180_REGISTER.MD)

        print(ac1, ac2, ac3, ac4, ac5, ac6, b1, b2, mb, mc, md)
        return BMP180_Calibration(ac1, ac2, ac3, ac4, ac5, ac6, b1, b2, mb, mc, md)

    def _readRawTemp(self):
        self._writeReg(BMP180_REGISTER.CONTROL, BMP180_COMMANDS.READ_TEMPERATURE.value, 0.005)
        raw = self._readU16BitInt(BMP180_REGISTER.DATA)
        return raw

    def _readRawPressure(self):
        delay = 0.005
        if self._mode == BMP180_MODE.HIGH_RESOLUTION or self._mode == BMP180_MODE.ULTRA_HIGH_RESOLUTION:
            delay = (2 + (3 << self._mode.value)) / 1000

        self._writeReg(BMP180_REGISTER.CONTROL, BMP180_COMMANDS.READ_PRESSURE.value | (self._mode.value << 6), delay)
        raw = self._readReg(BMP180_REGISTER.DATA, 3)
        return (raw[0] << 16 | raw[1] << 8 | raw[2]) >> (8 - self._mode.value)

    def _writeReg(self, register, value, wait = 0):
        self._i2cBus.write_byte_data(BMP180_I2CADDR, register.value, value)

        if wait > 0:
            time.sleep(wait)

    def _readU16BitInt(self, register):
        data = self._readReg(register, 2)
        return data[0] << 8 | data[1]

    def _read16BitInt(self, register):
        data = self._readReg(register, 2)
        if data[0] > 127:
            data[0] -= 256
        return data[0] << 8 | data[1]

    def _readReg(self, register, length):
        return self._i2cBus.read_i2c_block_data(BMP180_I2CADDR, register.value, length)