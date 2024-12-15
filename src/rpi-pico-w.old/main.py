# System Imports
import network
import utime
import json 
from time import sleep
from umqtt.simple import MQTTClient

# I/O Imports + BME280
import bme280
from machine import Pin,I2C

DEBUG = True

# Topics to publish
topic_inside_temp_living_room = "/home/inside/temperature_living_room"
topic_inside_humidity_living_room = "/home/inside/humidity_living_room"

# Freq to publish the topics
PUBLISH_FREQ = 15

# Wifi settings
ssid = 'FRITZ!Box 6660 Cable LQ'
password = '59231105902184626702'

# RPI Pico network settings
HOSTNAME = 'ashinkl-rpipw-3'  # Change for each new sensor
PORT = 12345

# Configure LED on the board as an output
led = Pin('LED', Pin.OUT)
led.value(False)

# Connect to WLAN 
wlan = network.WLAN(network.STA_IF)
network.hostname(HOSTNAME)
wlan.active(True)
led.value(True)
wlan.connect(ssid, password)
led.value(False)

# Initialize I2C to be able to read the BME280
i2c = I2C(0,sda=Pin(0), scl=Pin(1), freq=400000) 

# Connects to the Home Assistant MQTT Broker
def mqtt_connect():
    client = MQTTClient(client_id=b"python-mqtt-569",  # Change for each new sensor
                        server=b"homeassistant.local",
                        port=1883,
                        keepalive=3600,
                        user=b"mqtt-user",
                        password=b"mqtt-user"
                        )
    client.connect()
    return client

# Function to reboot the machine if the connection
# cannot be established
def reconnect():
    sleep(5)
    machine.reset()

# Function to get the sensor data and publish it to topics
def publish_topics():
  
        # Turn on the LED to show the program is running
        led.value(True)
                
        sensor_dictionary = {
            "Temperature_C":"NoData",
            "RelativePressure_hPa":"NoData",
            "Humidity_%":"NoData"
        }
 
        # Create opbject to get sensor data
        bme = bme280.BME280(i2c=i2c)
        if DEBUG:
            print(bme.values)
        

        # Toggle the LED to show a connection was accepted
        led.value(False)
        sleep(1)

        # Generate the data dictionary from the BME data
        sensor_dictionary["Temperature_C"] = round((9 * float(bme.values[0].split("C")[0].strip()))/5+32,1)
        sensor_dictionary["RelativePressure_hPa"] = float(bme.values[1].split("hPa")[0].strip())
        sensor_dictionary["Humidity_%"] = float(bme.values[2].split("%")[0].strip())
        
        # Send the string to the socket and close it
        client.publish(topic_inside_temp_living_room,str(sensor_dictionary["Temperature_C"]))
        client.publish(topic_inside_humidity_living_room,str(sensor_dictionary["Humidity_%"]))
        
# Try to connect to the MQTT broker
try:
    
    if DEBUG:
        print("try to connect to mqtt client")
    client = mqtt_connect()

# If not possible to connect, reboot
except OSError as e:
    reconnect()

# Try to publish data
try:
    
    # Publish topics
    while True:
       publish_topics()
       sleep(PUBLISH_FREQ)

# If Publish fails, reboot
except OSError as e:
    reconnect()


  
