# Documentation Links

|Topic|Link|
|-----|----|
|RPI Pinout|https://www.raspberrypi.com/documentation/computers/raspberry-pi.html|

To enable the one-wire interface you need to add the following line to /boot/config.txt, before rebooting your Pi:
dtoverlay=w1-gpio
