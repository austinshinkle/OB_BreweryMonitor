# system imports
import time
import socket
import threading
from DS18B20classfile import DS18B20
from array import array

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

# calibration data for sensor 2
SENSOR_2_OFFSET = -640729.2 #temp value
SENSOR_2_SCALE = 1/600 #temp value



# socket settings
host = "192.168.178.55"
port = 12345

# start socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host,port))
server_socket.listen(5)
print("Server listening on {}:{}".format(host,port))

# debug level 0 = none; 1 = verbose
DEBUG = 1

# set up the temp sensor data
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
				
		# write value of fermentation chamber 1 temperature
		if fermentation_chamber_1_installed:
			string = "FermentationChamberTemp1_C," + str(ferment_chamber_temp_sensor_1)
		else:
			string = "FermentationChamberTemp1_C," + "NotInstalled" 
			
		# write value of fermentation chamber 2 temperature		
		if fermentation_chamber_2_installed:
			string += ",FermentationChamberTemp2_C," + str(ferment_chamber_temp_sensor_2)
		else:
			 string += ",FermentationChamberTemp2_C," + "NotInstalled"
			 
		# write value of kegerator temperature		
		if kegerator_temp_sensor_installed:
			string += ",KegeratorTemp_C," + str(kegerator_temp_sensor)
		else:
			 string += ",KegeratorTemp_C," + "NotInstalled"
			 
		# write value of keg fill sensor 1
		if keg_fill_sensor_1_installed:
			string += ",KegWeightSensor1_PCT," + str(sensor_1_pct)
		else:
			 string += ",KegWeightSensor1_PCT," + "NotInstalled"
			 
		# write value of keg fill sensor 2
		if keg_fill_sensor_2_installed:
			string += ",KegWeightSensor2_PCT," + str(sensor_2_pct)
		else:
			 string += ",KegWeightSensor2_PCT," + "NotInstalled"

		client_socket.send(str.encode(string))
		
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
	
	while not terminate_thread:
	
		# add the temp sensor reading
		temp_cnt = 0
		
		if DEBUG:
			print('Getting the temp sensor data')
		
		# get all devices temperatures
		for temp_cnt in range(temp_device_count):
			
			device_temps.insert(temp_cnt,round(temp_devices.tempC(temp_cnt),2))
			if DEBUG:
				print(device_temps[temp_cnt])

		# if no errors, write the database
		if device_temps[0] < ERROR_DEVICE_TEMP and device_temps[1] < ERROR_DEVICE_TEMP:
			ferment_chamber_temp_sensor_1 = device_temps[0]
			ferment_chamber_temp_sensor_2 = device_temps[1]
			kegerator_temp_sensor = device_temps[2]
			
		time.sleep(1)

# function that measures the values of the weight sensors
# and stores the values in global variables
# designed to be run in a thread 
def measure_kegs():
	
	global terminate_thread
	global sensor_1_pct
	global sensor_2_pct
	
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
		if sensor_1_pct < 0:
			sensor_1_pct = 0
			
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
		if sensor_2_pct < 0:
			sensor_2_pct = 0
		
		### end sensor 2 ###
		
		# show the sensor values
		print(f"{sensor_1_pct}%,{sensor_2_pct}%")

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

	# start the thread to measure the kegs
	thread_measure_kegs = threading.Thread(target=measure_kegs)
	thread_measure_kegs.start()
	
	### FIX THIS LATER!!!! (not a good implementation)
	#time.sleep(5)
	
	
	thread_serve_data = threading.Thread(target=serve_data)
	thread_serve_data.start()
	
	thread_measure_temps = threading.Thread(target=measure_temps)
	thread_measure_temps.start()
	
	thread_serve_data.join()
	thread_measure_temps.join()
	thread_measure_kegs.join()
	
	
except KeyboardInterrupt:
	print('Script cancelled by user!')
	terminate_thread = True
	server_socket.close()
	time.sleep(2)
	GPIO.cleanup()
	
