import logging
import time
import socket  # Used for byte swapping to Big Endian

logger = logging.getLogger(__name__)

# ... get_i2c_device function stays the same ...
def get_i2c_device(address, i2c, i2c_bus):
    if i2c is not None:
        return i2c.get_i2c_device(address)
    else:
        import Adafruit_GPIO.I2C as I2C
        if i2c_bus is None:
            return I2C.get_i2c_device(address)
        else:
            return I2C.get_i2c_device(address, busnum=i2c_bus)


class INA219:
    # Registers
    __REG_CONFIG         = 0x00
    __REG_SHUNTVOLTAGE   = 0x01
    __REG_BUSVOLTAGE     = 0x02
    __REG_POWER          = 0x03
    __REG_CURRENT        = 0x04
    __REG_CALIBRATION    = 0x05

    def __init__(self, address=0x41, i2c=None, i2c_bus=7):
        self.i2c = get_i2c_device(address, i2c, i2c_bus)
        self.current_lsb = 0.1 # Default LSB for 32V/2A
        self.power_lsb = 2.0   # Default LSB for 32V/2A
        
        # Set default calibration (equivalent to ina219.begin() in Arduino)
        self.set_calibration_32V_2A()

    def _write_register_16(self, register, value):
        self.i2c.write16(register, socket.htons(value))

    def _read_register_16(self, register):
        # Read 16 bits and convert from Big Endian (BE)
        return socket.ntohs(self.i2c.readU16(register))
    
    def set_calibration_32V_2A(self):
        """Standard range: 32V, 2A"""
        self.current_lsb = 0.1 # 100uA per bit
        self.power_lsb = 2.0   # 2mW per bit
        self._write_register_16(self.__REG_CALIBRATION, 4096)
        
        # Config: 32V Range, +/-320mV Gain, 12-bit ADC
        self._write_register_16(self.__REG_CONFIG, 0x399F)

    def set_calibration_16V_400mA(self):
        """Higher precision: 16V, 400mA (from your Arduino code)"""
        # Calibration = trunc(0.04096 / (Current_LSB * Rshunt))
        # For 400mA range, Current_LSB = 0.05mA (50uA)
        self.current_lsb = 0.05 
        self.power_lsb = 1.0    # 1mW per bit
        self._write_register_16(self.__REG_CALIBRATION, 8192)
        
        # Config: 16V Range, +/-40mV Gain, 12-bit ADC
        self._write_register_16(self.__REG_CONFIG, 0x019F)

    def get_bus_voltage_v(self):
        # 1. Read the 16-bit register value and convert from Big Endian
        # We use the _read_register_16 helper we created earlier
        raw = self._read_register_16(self.__REG_BUSVOLTAGE)
        
        # 2. Shift the value right by 3 bits to remove CNVR and OVF flags
        # This leaves us with the 13-bit voltage value
        voltage_data = raw >> 3
        
        # 3. Multiply by the LSB (4mV or 0.004V) to get the actual voltage
        return voltage_data * 0.004
    
    def get_current_ma(self):
        raw = socket.ntohs(self.i2c.readU16(self.__REG_CURRENT))
        if raw > 32767: raw -= 65536
        return raw * self.current_lsb

    def get_power_mw(self):
        raw = socket.ntohs(self.i2c.readU16(self.__REG_POWER))
        return raw * self.power_lsb


# --- Test Usage ---
if __name__ == "__main__":
    # Note: Use i2c_bus=7 as confirmed by your i2cdetect scan
    sensor = INA219(address=0x41, i2c_bus=7)
    
    # To use high precision 16V/400mA:
    sensor.set_calibration_16V_400mA()
    
    while True:
        bus_v = sensor.get_bus_voltage_v()
        current = sensor.get_current_ma()
        
        print(f"Bus Voltage: {bus_v:.3f} V")
        print(f"Current:     {current:.3f} mA")
        print("-" * 20)
        time.sleep(1)