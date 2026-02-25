#!/usr/bin/env python3
import time, smbus2, math, socket

# =====================================================
# CONFIGURATION
# =====================================================
TCP_HOST = "192.168.1.30"   # Signal K or OpenPlotter host
TCP_PORT = 10110            # Default NMEA0183 TCP input
I2C_ADDRESSES = [0x40, 0x41, 0x42, 0x43]
SHUNT_RESISTANCE = 0.1
READ_INTERVAL = 2
SOURCE_ID = "INA219"
# =====================================================

bus = smbus2.SMBus(1)

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

def nmea_checksum(sentence):
    checksum = 0
    for char in sentence:
        checksum ^= ord(char)
    return f"{checksum:02X}"

def make_xdr(tag, value, units, name):
    """
    Example: $--XDR,A,0.45,P,PSEN,Sensor1*7C
    """
    body = f"IIXDR,{tag},{value:.3f},{units},{SOURCE_ID},{name}"
    return f"${body}*{nmea_checksum(body)}"

def send_to_signalk(nmea_sentences):
    try:
        with socket.create_connection((TCP_HOST, TCP_PORT), timeout=3) as sock:
            for sentence in nmea_sentences:
                sock.sendall((sentence + "\r\n").encode("ascii"))
    except Exception as e:
        print(f"⚠️  TCP send failed: {e}")

print(f"📡 Sending NMEA0183 XDR sentences to {TCP_HOST}:{TCP_PORT}")

while True:
    nmea_batch = []
    try:
        for i, addr in enumerate(I2C_ADDRESSES, start=1):
            try:
                vbus = get_bus_voltage_V(addr)
                vsh_mV = get_shunt_voltage_mV(addr)
                current = calc_current_A(vsh_mV)
                total_v = vbus + (vsh_mV / 1000.0)
                power = calc_power_W(total_v, current)

                nmea_batch.append(make_xdr("A", total_v, "V", f"V{i}"))
                nmea_batch.append(make_xdr("A", current, "A", f"I{i}"))
                nmea_batch.append(make_xdr("A", power, "W", f"P{i}"))

                print(f"INA{i}: {total_v:.3f}V {current:.3f}A {power:.3f}W")

            except Exception as e:
                print(f"⚠️  INA{i} read error: {e}")

        send_to_signalk(nmea_batch)
        time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        print("⛔ Stopped by user")
        break
