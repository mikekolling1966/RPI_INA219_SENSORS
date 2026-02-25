# RPI_INA219_SENSORS

INA219 multi-sensor bridge on Raspberry Pi, publishing readings to a Signal K server over WebSocket.

## Folder layout on the Pi

This repo is intended to live (or be copied to) the Raspberry Pi at:


/home/pi/Current-Power_Monitor_HAT/Current-Power_Monitor_HAT_Code/RaspberryPi


The main scripts are in that folder, for example:

- `ina219_to_signalk.py` – connects to Signal K WebSocket and sends updates
- `ina219_ws_bridge.py` – alternate WebSocket bridge implementation
- `verify_signalk.py` / `verify_and_logs.py` – quick connectivity checks

## systemd service location

The running service file is installed on the Pi at:


/etc/systemd/system/ina219.service


A copy is also stored in this repo for reference:


services/ina219.service


## Installing dependencies

Recommended: create a venv:

```bash
cd /home/pi/Current-Power_Monitor_HAT/Current-Power_Monitor_HAT_Code/RaspberryPi
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

If you do NOT use a venv, install globally:

sudo python3 -m pip install -r requirements.txt
Signal K configuration (host + token)

Do not hard-code tokens in the Python code.
Instead, use an environment file read by systemd.

Create:

/etc/default/ina219

Example:

sudo nano /etc/default/ina219

Contents:

SK_HOST=192.168.0.16
SK_PORT=3000
SK_TOKEN=PASTE_TOKEN_HERE
SK_CLIENT_ID=INA219-Monitor

Then update your script to read environment variables:

import os

SK_HOST = os.getenv("SK_HOST", "localhost")
SK_PORT = os.getenv("SK_PORT", "3000")
SK_TOKEN = os.getenv("SK_TOKEN", "")
SK_CLIENT_ID = os.getenv("SK_CLIENT_ID", "INA219-Monitor")

SIGNALK_WS = f"ws://{SK_HOST}:{SK_PORT}/signalk/v1/stream?clientId={SK_CLIENT_ID}"
Installing / updating the systemd service

Edit the service:

sudo nano /etc/systemd/system/ina219.service

Typical service file:

[Unit]
Description=INA219 to SignalK WebSocket Service
Wants=network-online.target
After=network-online.target

[Service]
User=pi
WorkingDirectory=/home/pi/Current-Power_Monitor_HAT/Current-Power_Monitor_HAT_Code/RaspberryPi
ExecStart=/usr/bin/python3 /home/pi/Current-Power_Monitor_HAT/Current-Power_Monitor_HAT_Code/RaspberryPi/ina219_to_signalk.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=/etc/default/ina219

# Logging (choose one approach)
StandardOutput=append:/var/log/ina219.log
StandardError=append:/var/log/ina219.err

[Install]
WantedBy=multi-user.target

Reload and restart:

sudo systemctl daemon-reload
sudo systemctl restart ina219.service

Enable on boot:

sudo systemctl enable ina219.service
Checking status and logs

Service status:

sudo systemctl status ina219.service

Logs (file-based):

sudo tail -n 200 /var/log/ina219.err
sudo tail -n 200 /var/log/ina219.log

Live:

sudo tail -f /var/log/ina219.err
Common issues
“Network is unreachable” / “Connection timed out”

Signal K host is not reachable. Check:

ping -c 3 192.168.0.16
nc -vz 192.168.0.16 3000
Token / auth issues

If you can reach the host but updates are rejected, generate a token on the target Signal K server and set SK_TOKEN in /etc/default/ina219.

I2C / sensor addresses

Check the INA219 devices are visible:

sudo i2cdetect -y 1

Expected addresses often include: 0x40 0x41 0x42 0x43


Save and exit.
