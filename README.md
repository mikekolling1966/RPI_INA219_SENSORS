# RPI_INA219_SENSORS

Raspberry Pi multi-INA219 sensor bridge publishing voltage, current and power readings to a Signal K server via WebSocket.

--------------------------------------------------------------------------------

PROJECT STRUCTURE

Live installation location on Sensors Pi:

/home/pi/Current-Power_Monitor_HAT/Current-Power_Monitor_HAT_Code

Python scripts are located in:

RaspberryPi/

Main script:

RaspberryPi/ina219_to_signalk.py

--------------------------------------------------------------------------------

SYSTEMD SERVICE (LIVE SYSTEM)

Installed service file:

/etc/systemd/system/ina219.service

The service executes:

/usr/bin/python3 /home/pi/Current-Power_Monitor_HAT/Current-Power_Monitor_HAT_Code/RaspberryPi/ina219_to_signalk.py

--------------------------------------------------------------------------------

EDITING THE PYTHON CODE

Edit the script:

nano /home/pi/Current-Power_Monitor_HAT/Current-Power_Monitor_HAT_Code/RaspberryPi/ina219_to_signalk.py

After editing:

sudo systemctl restart ina219.service

Check status:

sudo systemctl status ina219.service

--------------------------------------------------------------------------------

EDITING THE SYSTEMD SERVICE

Edit:

sudo nano /etc/systemd/system/ina219.service

After changes:

sudo systemctl daemon-reload
sudo systemctl restart ina219.service

Enable at boot:

sudo systemctl enable ina219.service

--------------------------------------------------------------------------------

SIGNAL K CONFIGURATION

Inside ina219_to_signalk.py:

SIGNALK_WS = "ws://192.168.0.16:3000/signalk/v1/stream?clientId=INA219-Monitor"
SIGNALK_TOKEN = "YOUR_TOKEN_HERE"

If changing Signal K server:

1. Update the IP address in SIGNALK_WS
2. Replace SIGNALK_TOKEN with a token generated on the target Signal K server
3. Restart the service

--------------------------------------------------------------------------------

LOG FILES

Current configuration logs to:

/var/log/ina219.log
/var/log/ina219.err

View recent errors:

sudo tail -n 200 /var/log/ina219.err

Live monitoring:

sudo tail -f /var/log/ina219.err

--------------------------------------------------------------------------------

CONNECTIVITY CHECKS

Check network:

ip a
ip route
ping -c 3 192.168.0.16
nc -vz 192.168.0.16 3000

Check I2C devices:

sudo i2cdetect -y 1

Expected INA219 addresses typically:

0x40 0x41 0x42 0x43

--------------------------------------------------------------------------------

COMMON ERRORS

Network is unreachable:
Signal K host not reachable from this Pi.

Connection timed out:
Signal K not running or wrong IP/port.

Authentication errors:
Token invalid or expired.

Service restart loop:
Check /var/log/ina219.err for traceback.

--------------------------------------------------------------------------------

DEPENDENCIES

Minimum requirement:

websocket-client

Install:

python3 -m pip install websocket-client

--------------------------------------------------------------------------------

SECURITY NOTE

Do not commit Signal K tokens into public repositories.

If publishing publicly, remove or externalise:

SIGNALK_TOKEN = "..."

--------------------------------------------------------------------------------

DEPLOYMENT CONTEXT

Designed for marine installation:
- Multiple INA219 sensors
- I2C bus 1
- Continuous WebSocket publishing to Signal K
- Managed via systemd for automatic restart

--------------------------------------------------------------------------------
