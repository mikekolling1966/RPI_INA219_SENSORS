#!/usr/bin/env python3
import requests, json

TARGET = "http://192.168.1.30:3000"

tests = [
    (f"{TARGET}/signalk", "Root capability"),
    (f"{TARGET}/signalk/v1/api", "API base"),
    (f"{TARGET}/signalk/v1/api/vessels/self", "Self vessel data (GET)"),
    (f"{TARGET}/signalk/v1/api/delta", "REST delta (POST)"),
    (f"{TARGET}/signalk/v1/api/_test/delta", "Legacy REST delta (POST)"),
    (f"{TARGET}/signalk/v1/stream", "WebSocket stream (HEAD)"),
]

def try_get(url):
    try:
        r = requests.get(url, timeout=3)
        return r.status_code, r.headers.get("Content-Type"), r.text[:100]
    except Exception as e:
        return "ERR", str(e), ""

def try_post(url):
    try:
        payload = {
            "context": "vessels.self",
            "updates": [{"values": [{"path": "electrical.test.voltage", "value": 12.34}]}],
        }
        r = requests.post(url, json=payload, timeout=3)
        return r.status_code, r.headers.get("Content-Type"), r.text[:100]
    except Exception as e:
        return "ERR", str(e), ""

print("=== Signal K Capability Probe ===\n")
for url, desc in tests:
    if "POST" in desc or "delta" in url:
        code, ctype, snippet = try_post(url)
    elif "stream" in url:
        try:
            r = requests.head(url, timeout=3)
            code, ctype, snippet = r.status_code, r.headers.get("Content-Type"), ""
        except Exception as e:
            code, ctype, snippet = "ERR", str(e), ""
    else:
        code, ctype, snippet = try_get(url)
    print(f"{desc:30} → {url}")
    print(f"  ↳ Status: {code}\n  ↳ Type:   {ctype}\n  ↳ Snip:   {snippet}\n")
