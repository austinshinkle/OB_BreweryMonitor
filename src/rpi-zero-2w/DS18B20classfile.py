import os
import glob
import time

class DS18B20:

	def __init__(self):
		os.system('modprobe w1-gpio')
		os.system('modprobe w1-therm')
		base_dir = '/sys/bus/w1/devices/'
		device_folder = glob.glob(base_dir + '28*')
		self._count_devices = len(device_folder)
		self._devices = list()

		i = 0
		while i < self._count_devices:
			self._devices.append(device_folder[i] + '/w1_slave')
			i += 1
			
			
	def device_names(self):

		names = list()

		for i in range(self._count_devices):
			names.append(self._devices[i])
			temp = names[i][20:35]
			names[i] = temp
		return names

	# (one tab)
	def _read_temp(self, index):

		try:
			f = open(self._devices[index], 'r')
			lines = f.readlines()
			f.close()
			return lines
		except FileNotFoundError:
			return None
			 


	def tempC(self, index = 0):

		lines = self._read_temp(index)
		retries = 5
		
		#if the temp read does not return a None (null) value
		if lines != None:
		
			try:
			
				while (lines[0].strip()[-3:] != 'YES') and (retries > 0):
					time.sleep(0.1)
					lines = self._read_temp(index)
					retries -= 1
					
					print(f"Retry counter: {retries}")
					
				if retries == 0:
					return 998

				equals_pos = lines[1].find('t=')

				if equals_pos != -1:
					temp = lines[1][equals_pos + 2:]
					return float(temp) / 1000
				else:
					return 999 # error
			except IndexError:
				print("Index out of range. Exiting function")
				return 998
		else:
			return 998

	def device_count(self):
		return self._count_devices
