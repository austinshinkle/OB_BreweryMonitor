# system imports
import time
import socket
import threading
from DS18B20classfile import DS18B20
from array import array

# INSTALLATION SETTINGS
fermentation_chamber_1_installed = True
fermentation_chamber_2_installed = True

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

def serve_data():
	
	global terminate_thread
	global ferment_chamber_temp_sensor_1
	global ferment_chamber_temp_sensor_2
	global fermentation_chamber_1_installed
	global fermentation_chamber_2_installed


	while not terminate_thread:
		client_socket, addr = server_socket.accept()
		if DEBUG:
				print("Got connection from", addr)

		if fermentation_chamber_1_installed and fermentation_chamber_2_installed:
			string = "FermentationChamberTemp1:" + str(ferment_chamber_temp_sensor_1) + ",FermentationChamberTemp2:" + str(ferment_chamber_temp_sensor_2)
		if fermentation_chamber_1_installed and not fermentation_chamber_2_installed:
			string = "FermentationChamberTemp1:" + str(ferment_chamber_temp_sensor_1) + ",FermentationChamberTemp2:" + "NotInstalled"
		if not fermentation_chamber_1_installed and fermentation_chamber_2_installed:
			string = "FermentationChamberTemp1:" + "NotInstalled" + ",FermentationChamberTemp2:" + str(ferment_chamber_temp_sensor_2)
		if not fermentation_chamber_1_installed and not fermentation_chamber_2_installed:
			string = "FermentationChamberTemp1:" + "NotInstalled" + ",FermentationChamberTemp2:" + "NotInstalled"

		client_socket.send(str.encode(string))
		
		client_socket.close()
		
		# Wait for keyboard input to terminate the thread
		#input("Press Enter to stop the program..\n")
		#terminate_thread = True

def measure_temps():
	
	global terminate_thread
	global ferment_chamber_temp_sensor_1
	global ferment_chamber_temp_sensor_2
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
			
		time.sleep(1)


# main program 
try:
	
	thread_serve_data = threading.Thread(target=serve_data)
	thread_serve_data.start()
	
	thread_measure_temps = threading.Thread(target=measure_temps)
	thread_measure_temps.start()
	
	thread_serve_data.join()
	
	
except KeyboardInterrupt:
	print('Script cancelled by user!')
	server_socket.close()
