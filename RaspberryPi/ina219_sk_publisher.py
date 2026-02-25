#!/usr/bin/env python3
import asyncio, json, time
from smbus2 import SMBus
import websockets

# =====================================================
# CONFIG
# =====================================================
I2C_ADDRESSES = [0x40, 0x41, 0x42, 0x43]
READ_INTERVAL = 2
SHUNT_RESISTANCE = 0.1
SOURCE_LABEL = "ina219-local"
HOST = "0.0.0.0"
PORT = 3000
# =====================================================

bus = SMBus(1)
clients = set()

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

async def sensor_loop():
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
            except Exception as e:
                print(f"INA{i} read error: {e}")

        msg = json.dumps(delta)
        for ws in list(clients):
            try:
                await ws.send(msg)
            except Exception:
                clients.discard(ws)
        await asyncio.sleep(READ_INTERVAL)

async def handler(websocket, path):
    print(f"✅ New Signal K subscriber from {websocket.remote_address}")
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.discard(websocket)

async def main():
    print(f"📡 Signal K micro-publisher active on ws://{HOST}:{PORT}/signalk/v1/stream")
    server = await websockets.serve(handler, HOST, PORT)
    await sensor_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user")
