import os
from os.path import isfile, join
import json

VERBOSE_OUTPUT = False

class JsonFileIO:

	def __init__(self):
		self.full_src_file_name = None
		return


	def print(self):
		print(" ~ Printing JsonFileIO ... ")
		print("	 Full Filename is: " + str(self.full_src_file_name))
	 

	def writeJsonFile(self, src_dir, filename, data):
		if (VERBOSE_OUTPUT):
			print(" ~ Writing data to JSON file: ", filename)

		self.full_src_file_name = os.path.join(src_dir, filename)
		
		self.createDirs(src_dir)

		with open(self.full_src_file_name, 'w') as json_file:
			json.dump(data, json_file, indent=4)
		
		if (VERBOSE_OUTPUT):	 
			print(" ~ JSON file written ...")

		return


	def readJsonFile(self, src_dir, filename):
		if (VERBOSE_OUTPUT):
			print(" ~ Reading data from JSON file: ", filename)
		
		self.full_src_file_name = os.path.join(src_dir, filename)

		# Determine if file exists
		file_exists = self.fileExists(self.full_src_file_name)
		if (file_exists):
			with open(self.full_src_file_name, 'r') as json_file:
				data_read = json.load(json_file)
	 
			if (VERBOSE_OUTPUT):
				print(" ~ JSON file data read:")
				print(data_read)

			return(data_read)
		else:
			print("\n ~ Error: file %s not found!" % self.full_src_file_name)
			print(" ~ Generate the missing file by running Sensor Calibration\n")
			return(-1)


	def getPathParts(self, file_path):
		if (VERBOSE_OUTPUT):
			print(" ~ Getting path parts ...")
		
		# Split the path in head and tail pair
		return os.path.split(file_path)
		  

	def getFileParts(self, file_name):
		if (VERBOSE_OUTPUT):
			print(" ~ Getting file parts ...")
		
		return file_name.split('.')


	def dirExists(self, dir_path):
		if (VERBOSE_OUTPUT):
			print(" ~ Determining if directory exists ...")
		
		return os.path.isdir(dir_path) 


	def createDirs(self, dir_path):
		if (VERBOSE_OUTPUT):
			print(" ~ Creating directory path ...")
		
		try:
			os.makedirs(dir_path, exist_ok = True)
			if (VERBOSE_OUTPUT):
				print(" ~ Directory '%s' created successfully" % dir_path)
		except OSError as error:
			print(" ~ Directory '%s' can not be created" % dir_path)

		return


	def fileExists(self, file_path):
		if (VERBOSE_OUTPUT):
			print(" ~ Determining if file exists ...")
		return os.path.isfile(file_path)
	
	
if __name__ == '__main__':

	print("\n ~ Exercising JsonFileIO Class ...")

	dir_basename = r'./'
	dir_folder_name = 'NewJsonFileIO_Test'
	filename = "test_file.json"
	dir_path = join(dir_basename, dir_folder_name)
	full_filename = join(dir_path, filename)

	print(dir_path)
	print(full_filename)

	mag_offsets = (1.0, 2.0, 3.0)
	gyro_offsets = (4.0, 5.0, 6.0)
	acel_offsets = (7.0, 8.0, 9.0)
		

	data = {
		"Offsets_Magnetometer" : mag_offsets,
		"Offsets_Gyroscope" : gyro_offsets,
		"Offsets_Accelerometer" : acel_offsets
	}

	JFIO = JsonFileIO()

	JFIO.writeJsonFile(dir_path, filename, data)
	read_data = JFIO.readJsonFile(dir_path, filename)

	# Verify the data
	exp_mag_offsets = list(mag_offsets)
	exp_gyro_offsets = list(gyro_offsets)
	exp_acel_offsets = list(acel_offsets)

	mag_data = read_data["Offsets_Magnetometer"]
	gyro_data = read_data["Offsets_Gyroscope"]
	acel_data = read_data["Offsets_Accelerometer"]
	
	assert(mag_data == exp_mag_offsets)
	assert(gyro_data == exp_gyro_offsets)
	assert(acel_data == exp_acel_offsets)
    
	print("\n ~ Fini! \n\n")