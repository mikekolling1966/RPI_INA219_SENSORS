#!/usr/bin/env python3
import subprocess
import requests
import json

# ===== CONFIGURATION =====
SIGNALK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImluYTIxOS1zY3JpcHQiLCJwZXJtaXNzaW9ucyI6WyJyZWFkIiwid3JpdGUiXSwiaWF0IjoxNzYxODQ3NTM4LCJleHAiOjIwNzc0MjM1Mzh9.ngapx4aHza7xZYh5aICJIeExWgNmKNlJXRKnssCthuk"
SIGNALK_API = "http://localhost:3000/signalk/v1/api/vessels/self"
LOG_LINES = 100  # Number of log lines to read
# =========================

def verify_token():
    print("✅ Testing Signal K REST API with token...")
    headers = {"Authorization": f"Bearer {SIGNALK_TOKEN}"}
    try:
        response = requests.get(SIGNALK_API, headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Token is valid. REST API returned data:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Token rejected. HTTP {response.status_code}")
            print("Response:", response.text)
            return False
    except Exception as e:
        print(f"❌ Error connecting to Signal K API: {e}")
        return False

def read_logs():
    print(f"\n📜 Reading last {LOG_LINES} lines of Signal K logs...")
    try:
        logs = subprocess.check_output(
            ["journalctl", "-u", "signalk", f"-n{LOG_LINES}", "--no-pager"],
            text=True
        )
        filtered = [line for line in logs.splitlines() if "JWT" in line or "unauthorized" in line or "security" in line]
        if filtered:
            print("\n🔍 Security-related log entries:")
            for line in filtered:
                print(line)
        else:
            print("✅ No security/authentication errors found in logs.")
    except Exception as e:
        print(f"❌ Error reading logs: {e}")

if __name__ == "__main__":
    print("=== Signal K Token & Log Verification ===")
    token_ok = verify_token()
    read_logs()
    if not token_ok:
        print("\n⚠️ Token invalid or rejected. Check user permissions and regenerate token.")
