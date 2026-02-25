#!/usr/bin/env python3
import asyncio, json, time, logging
from smbus2 import SMBus
import websockets

SIGNALK_WS = "ws://192.168.1.30:3000/signalk/v1/stream"
I2C_ADDRESSES = [0x40, 0x41, 0x42, 0x43]
READ_INTERVAL = 2
SHUNT_RESISTANCE = 0.1
LOG_FILE = "/home/pi/ina219_bridge.log"

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

async def send_loop():
    while True:
        try:
            print(f"Connecting to {SIGNALK_WS} ...")
            async with websockets.connect(SIGNALK_WS) as ws:
                print("✅ Connected to Signal K stream")
                logging.info("Connected to Signal K stream")

                while True:
                    delta = {
                        "context": "vessels.self",
                        "updates": [
                            {
                                "source": {"label": "rpi-ina219-bridge"},
                                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                "values": []
                            }
                        ]
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
                            logging.error(f"INA{i} read error: {e}")
                            print(f"INA{i} read error: {e}")

                    await ws.send(json.dumps(delta))
                    await asyncio.sleep(READ_INTERVAL)
        except Exception as e:
            print(f"⚠️  WebSocket error: {e}")
            logging.error(f"WebSocket error: {e}")
            print("Reconnecting in 5 s …")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(send_loop())
    except KeyboardInterrupt:
        print("Stopped by user")
        logging.info("Stopped by user")
