import smbus
import time
import json
import websocket

# INA219 Register Definitions
_REG_CONFIG = 0x00
_REG_SHUNTVOLTAGE = 0x01
_REG_BUSVOLTAGE = 0x02
_REG_POWER = 0x03
_REG_CURRENT = 0x04
_REG_CALIBRATION = 0x05

class BusVoltageRange:
    RANGE_16V = 0x00
    RANGE_32V = 0x01

class Gain:
    DIV_1_40MV = 0x00
    DIV_2_80MV = 0x01
    DIV_4_160MV = 0x02
    DIV_8_320MV = 0x03

class ADCResolution:
    ADCRES_12BIT_32S = 0x0D
class Mode:
    SANDBVOLT_CONTINUOUS = 0x07

class INA219:
    def __init__(self, i2c_bus=1, addr=0x40):
        self.bus = smbus.SMBus(i2c_bus)
        self.addr = addr
        self._cal_value = 4096
        self._current_lsb = 0.1
        self._power_lsb = 0.002
        self.set_calibration_32V_2A()

    def read(self, address):
        data = self.bus.read_i2c_block_data(self.addr, address, 2)
        return (data[0] << 8) + data[1]

    def write(self, address, data):
        temp = [(data >> 8) & 0xFF, data & 0xFF]
        self.bus.write_i2c_block_data(self.addr, address, temp)

    def set_calibration_32V_2A(self):
        self.write(_REG_CALIBRATION, self._cal_value)
        config = (BusVoltageRange.RANGE_32V << 13 |
                  Gain.DIV_8_320MV << 11 |
                  ADCResolution.ADCRES_12BIT_32S << 7 |
                  ADCResolution.ADCRES_12BIT_32S << 3 |
                  Mode.SANDBVOLT_CONTINUOUS)
        self.write(_REG_CONFIG, config)

    def getShuntVoltage_mV(self):
        self.write(_REG_CALIBRATION, self._cal_value)
        value = self.read(_REG_SHUNTVOLTAGE)
        if value > 32767:
            value -= 65535
        return value * 0.01

    def getBusVoltage_V(self):
        self.write(_REG_CALIBRATION, self._cal_value)
        value = self.read(_REG_BUSVOLTAGE)
        return (value >> 3) * 0.004

    def getCurrent_mA(self):
        value = self.read(_REG_CURRENT)
        if value > 32767:
            value -= 65535
        return value * self._current_lsb

    def getPower_W(self):
        value = self.read(_REG_POWER)
        if value > 32767:
            value -= 65535
        return value * self._power_lsb

# Signal K WebSocket details
SIGNALK_WS = "ws://192.168.1.30:3000/signalk/v1/stream"
SIGNALK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6InBpIiwiaWF0IjoxNzYyMDI3MzcyLCJleHAiOjE3OTM1ODQ5NzJ9.MptmLFnk2Ne0mT8BmwrFQ69JulcIKOwESA2kfca4rWs"

# label mapping

sensor_labels = {
    0: ("INA4", "sensors.port.oilpressure.voltage"),
    1: ("INA3", "sensors.starboard.oilpressure.voltage"),
    2: ("INA2", "sensors.port.watertemp.voltage"),
    3: ("INA1", "sensors.starboard.watertemp.voltage")
}





def send_to_signalk(ws, sensor_id, voltage, current, power):
    label, path = sensor_labels[sensor_id]
    data = {
        "updates": [
            {
                "source": {"label": label},
                "values": [
                    {"path": path, "value": voltage},
                    {"path": path.replace("Voltage", "Current"), "value": current},
                    {"path": path.replace("Voltage", "Power"), "value": power}
                ]
            }
        ]
    }
    ws.send(json.dumps(data))

if __name__ == '__main__':
    ws = websocket.WebSocket()
    ws.connect(SIGNALK_WS, header=[f"Authorization: Bearer {SIGNALK_TOKEN}"])
    print("✅ Connected to Signal K WebSocket")

    ina_sensors = [
        INA219(addr=0x40),
        INA219(addr=0x41),
        INA219(addr=0x42),
        INA219(addr=0x43)
    ]

    while True:
        for i, sensor in enumerate(ina_sensors):
            bus_voltage = sensor.getBusVoltage_V()
            shunt_voltage = sensor.getShuntVoltage_mV() / 1000
            current = sensor.getCurrent_mA() / 1000
            power = sensor.getPower_W()
            psu_voltage = bus_voltage + shunt_voltage

            label, path = sensor_labels[i]
            print(f"{label}: {path} = {psu_voltage:.3f} V, Current={current:.3f} A, Power={power:.3f} W")
            send_to_signalk(ws, i, psu_voltage, current, power)

        time.sleep(2)
