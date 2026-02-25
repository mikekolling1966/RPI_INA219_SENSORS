#!/usr/bin/env python3
import json, time, requests, logging
from smbus2 import SMBus

# =====================================================
# CONFIGURATION
# =====================================================
SIGNALK_API = "http://192.168.1.30:3000/signalk/v1/api/_test/delta"
I2C_ADDRESSES = [0x40, 0x41, 0x42, 0x43]
READ_INTERVAL = 2
SHUNT_RESISTANCE = 0.1
LOG_FILE = "/home/pi/ina219_bridge.log"
SOURCE_LABEL = "INA219 REST bridge for remote RPi"
# =====================================================

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

bus = SMBus(1)

def read_word(addr, reg):
    data = bus.read_i2c_block_data(addr, reg, 2)
    return (data[0] << 8) + data[1]

def get_bus_voltage_V(addr):
    value = read_word(addr, 0x02)
    return (value >> 3) * 0.004

def get_shunt_voltage_mV(addr):
    value = read_word(addr, 0x01)
    if value > 32767:
        value -= 65536
    return value * 0.01

def calc_current_A(vsh_mV):
    return (vsh_mV / 1000.0) / SHUNT_RESISTANCE

def calc_power_W(vbus, current):
    return vbus * current

def post_delta(delta):
    try:
        r = requests.post(SIGNALK_API, json=delta, timeout=5)
        if r.status_code != 200:
            logging.warning(f"POST failed: {r.status_code} {r.text}")
        else:
            logging.info(f"POST OK: {r.status_code}")
    except Exception as e:
        logging.error(f"POST error: {e}")

print(f"📡 Posting to {SIGNALK_API}")
while True:
    delta = {
        "context": "vessels.self",
        "updates": [{
            "source": {"label": SOURCE_LABEL},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "values": []
        }]
    }

    for i, addr in enumerate(I2C_ADDRESSES, start=1):
        try:
            vbus = get_bus_voltage_V(addr)
            vsh_mV = get_shunt_voltage_mV(addr)
            current = calc_current_A(vsh_mV)
            total_v = round(vbus + (vsh_mV / 1000.0), 3)
            power = calc_power_W(total_v, current)

            delta["updates"][0]["values"].extend([
                {"path": f"electrical.ina{i}.voltage", "value": total_v},
                {"path": f"electrical.ina{i}.current", "value": round(current, 3)},
                {"path": f"electrical.ina{i}.power", "value": round(power, 3)}
            ])

            msg = f"INA{i}: V={total_v:.3f}V I={current:.3f}A P={power:.3f}W"
            print(msg)
            logging.info(msg)

        except Exception as e:
            err = f"INA{i} read error: {e}"
            print(err)
            logging.error(err)

    post_delta(delta)
    time.sleep(READ_INTERVAL)
