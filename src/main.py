# System Imports
import network
import socket
import json 
from time import sleep

# I/O Imports + BME280
import bme280
from machine import Pin,I2C

DEBUG = False

# Wifi settings
ssid = 'FRITZ!Box 6660 Cable LQ'
password = '59231105902184626702'

HOSTNAME = 'ashinkl-rpipw'
PORT = 12345

wlan = network.WLAN(network.STA_IF)

# Configure LED on the board as an output
led = Pin('LED', Pin.OUT)
led.value(False)

# Initialize I2C to be able to read the BME280
i2c = I2C(0,sda=Pin(0), scl=Pin(1), freq=400000) 

# Function to initialize the wifi connection
def init_wifi():   
    
    global wlan
    
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    network.hostname(HOSTNAME)
    wlan.active(True)
    wlan.connect(ssid, password)

# Function to connect to the wifi
def connect_to_wifi():
    
    global wlan
    
    # Wait for the wifi connetion
    while wlan.isconnected() == False:
        if DEBUG:
            print('Waiting for connection...')
        led.value(True)
        sleep(.25)
        led.value(False)
        sleep(.25)
    ip = wlan.ifconfig()[0]
    return ip

# Function to open a socket
def open_socket(ip, port):
    
    # Open a socket
    address = (ip, port)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(5)
    return(connection)

# Function to start a web server
def serve_connection(connection):
  
    while True:
                
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
        
        # Accept incoming connections
        client_socket, addr = connection.accept()

        # Toggle the LED to show a connection was accepted
        led.value(False)
        sleep(1)

        # Generate the data dictionary from the BME data
        sensor_dictionary["Temperature_C"] = float(bme.values[0].split("C")[0].strip())
        sensor_dictionary["RelativePressure_hPa"] = float(bme.values[1].split("hPa")[0].strip())
        sensor_dictionary["Humidity_%"] = float(bme.values[2].split("%")[0].strip())
        
        # Send the string to the socket and close it
        client_socket.send(str.encode(json.dumps(sensor_dictionary)))
        client_socket.close()

# Main program
try:
    
    init_wifi()
    
    while True:
        if wlan.isconnected() == False
            ip = connect_to_wifi()
        connection = open_socket(ip,PORT)
        serve_connection(connection)
    
except KeyboardInterrupt:
    machine.reset()

  
