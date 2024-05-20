# Documentation Links

|Topic|Link|
|-----|----|
|RPI Pinout|https://www.raspberrypi.com/documentation/computers/raspberry-pi.html|
|iBeacon|https://kvurd.com/blog/tilt-hydrometer-ibeacon-data-format/|

## Enable 1 Wire Interface on RPI
To enable the one-wire interface you need to add the following line to /boot/firmware/config.txt, before rebooting your Pi:
dtoverlay=w1-gpio

## Start a process via SSH and persist after closing the session
```
nohup python3 measure_sensors.py
```

## Stop a process running in the background
Get PID and kill that PID
```
ps -ef | grep python3
kill -9 <PID>
```


## Seek Lite BT-LE MAC Address
01:B6:EC:D9:CD:62 SEEK-LITE
