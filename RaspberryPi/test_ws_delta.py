#!/usr/bin/env python3
import asyncio, websockets, json

async def main():
    uri = "ws://192.168.1.30:3000/signalk/v1/stream"
    print(f"Connecting to {uri}")
    async with websockets.connect(uri) as ws:
        print("Connected. Sending test delta …")
        delta = {
            "context": "vessels.self",
            "updates": [
                {
                    "source": {"label": "rpi-test"},
                    "values": [
                        {"path": "electrical.test.voltage", "value": 12.34}
                    ]
                }
            ]
        }
        await ws.send(json.dumps(delta))
        print("Sent delta; waiting 2 s …")
        await asyncio.sleep(2)

asyncio.run(main())
