#!/usr/bin/env python3
import time, json, os, requests
from smbus2 import SMBus

# === CONFIG ===
SIGNALK = "http://192.168.1.30:3000"
TOKEN_FILE = "/home/pi/.signalk_token"
ADDRS = [0x40, 0x41, 0x42, 0x43]
SHUNT = 0.1
INTERVAL = 2
# ===============

def get_token():
    if os.path.exists(TOKEN_FILE):
        return open(TOKEN_FILE).read().strip()

    print("🔑 Requesting new Signal K access token…")
    r = requests.post(f"{SIGNALK}/signalk/v1/requests", timeout=5)
    if r.status_code == 202:
        req = r.json()
        print(f"⚠️  Approve in Signal K: Admin → Security → Access Requests → {req.get('requestId')}")
        print("Then re-run this script after approval.")
        return None
    else:
        print("❌ Token request failed:", r.text)
        return None

def write_token(t):
    open(TOKEN_FILE, "w").write(t.strip())

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
token = get_token()
if not token:
    exit()

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print("📡 Sending INA219 data via PUT every", INTERVAL, "s")

while True:
    for i, a in enumerate(ADDRS, 1):
        try:
            vb = bus_voltage(bus, a)
            vsh = shunt_mV(bus, a)
            cur = current_A(vsh)
            vtot = round(vb + (vsh / 1000.0), 3)
            pwr = power_W(vtot, cur)

            base = f"{SIGNALK}/signalk/v1/api/vessels/self/electrical.ina{i}"
            requests.put(f"{base}.voltage", headers=headers, json={"value": vtot})
            requests.put(f"{base}.current", headers=headers, json={"value": cur})
            requests.put(f"{base}.power", headers=headers, json={"value": pwr})

            print(f"INA{i}: V={vtot:.3f} V  I={cur:.3f} A  P={pwr:.3f} W")
        except Exception as e:
            print("⚠️ INA", i, "error:", e)

    time.sleep(INTERVAL)
