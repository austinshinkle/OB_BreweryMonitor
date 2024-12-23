# system imports
import time
import socket
import json
import threading
from DS18B20classfile import DS18B20
from array import array

from paho.mqtt import client as mqtt_client

# weight sensor imports
from hx711 import HX711
import RPi.GPIO as GPIO

# INSTALLATION SETTINGS
fermentation_chamber_1_installed = True
fermentation_chamber_2_installed = True
keg_fill_sensor_1_installed = True
keg_fill_sensor_2_installed = True
kegerator_temp_sensor_installed = True

# samples that should be taken for each sensor
SAMPLES = 5

# calibration data for sensor 1
SENSOR_1_OFFSET = -519856.2 #temp value
SENSOR_1_SCALE = 1/1000 #temp value
#SENSOR_1_OFFSET = 6748575 #temp value
#SENSOR_1_SCALE = 1/337.248 #temp value  

# calibration data for sensor 2
SENSOR_2_OFFSET = -640729.2 #temp value
SENSOR_2_SCALE = 1/600 #temp value
#SENSOR_2_OFFSET = 6748575 #temp value
#SENSOR_2_SCALE = 1/337.248 #temp value  

# defines to determine how long to wait to write data
GET_SENSOR_DATA_FREQ = 15 #55
MQTT_WRITE_FREQ = 20 #60

new_data_avail = False

# socket settings
host = "192.168.178.75"
port = 12345

# mqtt settings
broker = 'homeassistant.local'
port = 1883
topic_inside_temp = "/home/inside/temperature"
client_id = f'python-mqtt-543'
username = 'mqtt-user'

# start socket
#server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#server_socket.bind((host,port))
#server_socket.listen(5)
#print("Server listening on {}:{}".format(host,port))

# debug level 0 = none; 1 = verbose
DEBUG = 1

degree_sign = u'\xb0'
temp_devices = DS18B20()
temp_device_count = temp_devices.device_count()
if DEBUG:
	print(f'Found {temp_device_count} devices')
temp_device_names = temp_devices.device_names()
ERROR_DEVICE_TEMP = 200

device_temps = array('d', [])
	
# global variables to communicate between threads
terminate_thread = False
ferment_chamber_temp_sensor_1 = 0
ferment_chamber_temp_sensor_2 = 0
sensor_1_pct = 0
sensor_2_pct = 0
kegerator_temp_sensor = 0



# function that creates and starts the mqtt connection
def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):

        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    client.username_pw_set(username, username)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


# function that get the received
# values from the global variables
# and writes them to an MQTT broker
# designed to be run in a thread 
def write_data_to_mqtt():
	
	global terminate_thread
	global keg_level_1
	global keg_level_2
	global fermentation_chamber_temp_1
	global fermentation_chamber_temp_2
	global kegerator_temp
	global outside_temp
	global outside_pressure
	global outside_humidity
	global new_data_avail

	while not terminate_thread:
		
		print("Running Thread: write_data_to_mqtt")

		try:

			# only write data if it is not stale
			if new_data_avail:

				if DEBUG > 1:
					print("Writing values to MQTT...")
				
				result = client.publish(topic_inside_temp, str(ferment_chamber_temp_sensor_1)) 
		
				# set the data to stale
				new_data_avail = False

		except ConnectionRefusedError:
			print("Cannot connect to server...will try again later.")
		
		finally:
			time.sleep(MQTT_WRITE_FREQ)

def serve_data():
	
	global terminate_thread
	global ferment_chamber_temp_sensor_1
	global ferment_chamber_temp_sensor_2
	global kegerator_temp_sensor
	global sensor_1_pct
	global sensor_2_pct
	global fermentation_chamber_1_installed
	global fermentation_chamber_2_installed
	global keg_fill_sensor_1_installed
	global keg_fill_sensor_2_installed
	global kegerator_temp_sensor_installed


	while not terminate_thread:
		client_socket, addr = server_socket.accept()
		if DEBUG:
				print("Got connection from", addr)
		
		# create sensor dictionary with default values
		sensor_dictionary = {
			"FermentationChamberTemp1_F":"NoData",
			"FermentationChamberTemp2_F":"NoData",
			"KegeratorTemp_F":"NoData",
			"KegWeightSensor1_PCT":"NoData",
			"KegWeightSensor2_PCT":"NoData"
		}
				
		# write value of fermentation chamber 1 temperature
		if fermentation_chamber_1_installed:
			sensor_dictionary["FermentationChamberTemp1_F"] = ferment_chamber_temp_sensor_1
			
		# write value of fermentation chamber 2 temperature		
		if fermentation_chamber_2_installed:		
			sensor_dictionary["FermentationChamberTemp2_F"] = ferment_chamber_temp_sensor_2
			 
		# write value of kegerator temperature		
		if kegerator_temp_sensor_installed:
			sensor_dictionary["KegeratorTemp_F"] = kegerator_temp_sensor
			 
		# write value of keg fill sensor 1
		if keg_fill_sensor_1_installed:
			sensor_dictionary["KegWeightSensor1_PCT"] = sensor_1_pct
			 
		# write value of keg fill sensor 2
		if keg_fill_sensor_2_installed:
			sensor_dictionary["KegWeightSensor2_PCT"] = sensor_2_pct

		client_socket.send(str.encode(json.dumps(sensor_dictionary)))
		client_socket.close()
		
		# Wait for keyboard input to terminate the thread
		#input("Press Enter to stop the program..\n")
		#terminate_thread = True

def measure_temps():
	
	global terminate_thread
	global ferment_chamber_temp_sensor_1
	global ferment_chamber_temp_sensor_2
	global kegerator_temp_sensor
	global temp_device_count
	global new_data_avail
	
	while not terminate_thread:
	
		# add the temp sensor reading
		temp_cnt = 0
		
		if DEBUG:
			print('Getting the temp sensor data')
		
		# get all devices temperatures
		for temp_cnt in range(temp_device_count):
			
			device_temps.insert(temp_cnt,round((9/5 * temp_devices.tempC(temp_cnt))+32,1))
			if DEBUG:
				print(device_temps[temp_cnt])

		# if no errors, write the database
		if device_temps[0] < ERROR_DEVICE_TEMP and device_temps[1] < ERROR_DEVICE_TEMP:
			ferment_chamber_temp_sensor_1 = device_temps[0]
			ferment_chamber_temp_sensor_2 = device_temps[1]
			kegerator_temp_sensor = device_temps[2]
			
		new_data_avail = True

		time.sleep(1)

# function that measures the values of the weight sensors
# and stores the values in global variables
# designed to be run in a thread 
def measure_kegs():
	
	global terminate_thread
	global sensor_1_pct
	global sensor_2_pct
	global new_data_avail
	
	while not terminate_thread:
		
		### sensor 1 ###
		
		# measure sensor values
		sensor_1_measures = hx711.get_raw_data(times=SAMPLES)
		
		# get average of all sensor values
		sensor_1_raw = 0
		for x in range(SAMPLES):
			sensor_1_raw += sensor_1_measures[x]
			x += 1
		sensor_1_raw /= SAMPLES
		
		# apply scale and offset --> percent
		sensor_1_pct = int(SENSOR_1_SCALE * (sensor_1_raw - SENSOR_1_OFFSET))
		#sensor_1_pct = 27 #dummy value
#		if sensor_1_pct < 0:
#			sensor_1_pct = 0
			
		### end sensor 1 ###
		
		### sensor 2 ###	
		
		# measure sensor values
		sensor_2_measures = hx711_2.get_raw_data(times=SAMPLES)
		
		# get average of all sensor values
		sensor_2_raw = 0
		for x in range(SAMPLES):
			sensor_2_raw += sensor_2_measures[x]
			x += 1
		sensor_2_raw /= SAMPLES
		
		# apply scale and offset --> percent
		sensor_2_pct = int(SENSOR_2_SCALE * (sensor_2_raw - SENSOR_2_OFFSET))
		#sensor_2_pct = 85 #dummy value

#		if sensor_2_pct < 0:
#			sensor_2_pct = 0
		
		### end sensor 2 ###
		
		# show the sensor values
		print(f"{sensor_1_pct}%,{sensor_2_pct}%")

		new_data_avail = True

		time.sleep(.5)

# main program 
try:
			
	# channel A for amplifier board @ 128 gain for maximum signal swing
	hx711 = HX711(
		dout_pin=5,
		pd_sck_pin=6,
		channel='A',
		gain=128
	)			
	
	# channel A for amplifier board @ 128 gain maximum signal swing
	hx711_2 = HX711(
		dout_pin=9,
		pd_sck_pin=10,
		channel='A',
		gain=128
	)
	
	# reset the devices
	hx711.reset()   # Before we start, reset the HX711 (not obligate)	
	hx711_2.reset()   # Before we start, reset the HX711 (not obligate)

	# connect to the mqtt broker
	client = connect_mqtt()

	# start the thread to measure the kegs
	thread_measure_kegs = threading.Thread(target=measure_kegs)
	thread_measure_kegs.start()

	# start the thread to measure the temperatures
	thread_measure_temps = threading.Thread(target=measure_temps)
	thread_measure_temps.start()
		
	# start the thread to serve the data
	thread_write_data_to_mqtt = threading.Thread(target=write_data_to_mqtt)
	thread_write_data_to_mqtt.start()
	
	# set up the threads to allow them to finish on script termination
	thread_write_data_to_mqtt.join()
	thread_measure_temps.join()
	thread_measure_kegs.join()
	
	
except KeyboardInterrupt:
	print('Script cancelled by user!')
	terminate_thread = True
	time.sleep(2)
	GPIO.cleanup()
	
