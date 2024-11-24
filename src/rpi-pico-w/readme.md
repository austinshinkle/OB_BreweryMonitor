# Software Setup for RPI Pico W

## 1. Download Micropython firmware to RPI Pico W
Put the device into BOOT mode and copy the correct UF2 file (named something like RPI_PICO_W-20241025-v1.24.0.uf2) onto the system. If this is a new RPI Pico W, it will automatically start in BOOT mode. Additional instructions can be found on the official Raspberry Pi website <https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython>

## 2. Install the BME 280 micropython library
From Thonny, go to "Tools...Manage packages...", search for "micropython-bme280" and install it

## 3. Install the umqtt.simple micropython library
From Thonny, go to "Tools...Manage packages...", search for "micropython-umqtt.simple" and install it

## 4. Copy main.py onto the target
From Thonny, go to "File...Save as...", select the Raspberry Pi Pico and save the file to the main folder

# Additional Notes

## Home Assistant Setup
The configuratin.yaml file in Home Assistant must be updated to connect the MQTT topics to Home Assistant
### Current MQTT Topic List
- /home/inside/temperature
- /home/outside/temperature
- /home/outside/humidity
- /home/inside/temperature_bedroom
- /home/inside/humidity_bedroom

### Example configuration.yaml
```
mqtt:
  sensor:
    - name: "Inside Temperature"
      unique_id: "sensor.inside_temp"
      state_topic: "/home/inside/temperature"  
      device_class: "temperature"
      unit_of_measurement: "°F"
      suggested_display_precision: 1
    - name: "Outside Temperature"
      unique_id: "sensor.outside_temp"
      state_topic: "/home/outside/temperature"
      device_class: "temperature"
      unit_of_measurement: "°F"
      suggested_display_precision: 1
    - name: "Outside Humidity"
      unique_id: "sensor.outside_humidity"
      state_topic: "/home/outside/humidity"
      device_class: "humidity"
      suggested_display_precision: 1
    - name: "Inside Temperature - Bedroom"
      unique_id: "sensor.inside_temp_bedroom"
      state_topic: "/home/inside/temperature_bedroom"
      device_class: "temperature"
      unit_of_measurement: "°F"
      suggested_display_precision: 1
    - name: "Inside Humidity - Bedroom"
      unique_id: "sensor.inside_humidity_bedroom"
      state_topic: "/home/inside/humidity_bedroom"
      device_class: "humidity"
      suggested_display_precision: 1
```
