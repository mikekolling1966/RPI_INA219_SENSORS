#!/usr/bin/env python3
import json, socket, time
from smbus2 import SMBus

SK_HOST = "192.168.1.30"
SK_PORT = 8375
ADDRS = [0x40, 0x41, 0x42, 0x43]
SHUNT = 0.1
INTERVAL = 2

def read_word(bus, addr, reg):
    data = bus.read_i2c_block_data(addr, reg, 2)
    return (data[0] << 8) + data[1]

def bus_voltage(bus, addr):
    val = read_word(bus, addr, 0x02)
    return (val >> 3) * 0.004

def shunt_mV(bus, addr):
    val = read_word(bus, addr, 0x01)
    if val > 32767: val -= 65536
    return val * 0.01

def current_A(vsh):
    return (vsh / 1000.0) / SHUNT

def power_W(vbus, current):
    return vbus * current

bus = SMBus(1)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SK_HOST, SK_PORT))
print(f"✅ Connected to Signal K TCP input at {SK_HOST}:{SK_PORT}")

while True:
    delta = {
        "context": "vessels.self",
        "updates": [{"source": {"label": "ina219-tcp-bridge"}, "values": []}]
    }

    for i, a in enumerate(ADDRS, 1):
        try:
            vb = bus_voltage(bus, a)
            vsh = shunt_mV(bus, a)
            cur = current_A(vsh)
            vtot = round(vb + (vsh / 1000.0), 3)
            pwr = power_W(vtot, cur)
            delta["updates"][0]["values"].extend([
                {"path": f"electrical.ina{i}.voltage", "value": vtot},
                {"path": f"electrical.ina{i}.current", "value": cur},
                {"path": f"electrical.ina{i}.power", "value": pwr}
            ])
            print(f"INA{i}: {vtot:.3f}V {cur:.3f}A {pwr:.3f}W")
        except Exception as e:
            print(f"INA{i} error:", e)

    sock.send((json.dumps(delta) + "\n").encode())
    time.sleep(INTERVAL)
