#!/usr/bin/env python3
import socketserver
import time
import random
import threading

def nmea_checksum(sentence):
    checksum = 0
    for char in sentence:
        checksum ^= ord(char)
    return f"{checksum:02X}"

class EW10Handler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"✅ Client connected: {self.client_address}")
        try:
            while True:
                volt = round(12.0 + random.uniform(-0.05, 0.05), 3)
                curr = round(0.5 + random.uniform(-0.05, 0.05), 3)
                power = round(volt * curr, 3)

                raw_sentences = [
                    f"IIXDR,A,{volt},V,INA1,VOLT",
                    f"IIXDR,A,{curr},A,INA1,CURR",
                    f"IIXDR,A,{power},W,INA1,POWR"
                ]

                for raw in raw_sentences:
                    checksum = nmea_checksum(raw)
                    sentence = f"${raw}*{checksum}\r\n"
                    self.request.sendall(sentence.encode())
                    time.sleep(0.3)

                time.sleep(1.5)
        except (BrokenPipeError, ConnectionResetError):
            print(f"⚠️ Client disconnected: {self.client_address}")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
HOST = "0.0.0.0"
PORT = 8899
print(f"📡 Multi-client EW10 emulator listening on {HOST}:{PORT}")

with ThreadedTCPServer((HOST, PORT), EW10Handler) as server:
    server.serve_forever()
