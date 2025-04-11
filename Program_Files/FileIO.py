import os
from os import listdir
from os.path import isfile, join

VERBOSE_OUTPUT = False

class FileIO:

	def __init__(self):
		self.fid = None
		self.full_src_file_name = None
		return


	def print(self):
		print(" ~ Printing FileIO ... ")
		print("	 FID is: " + str(self.fid))
		print("	 Full Filename is: " + str(self.full_src_file_name))
	  

	def createFile(self, filename):
		if (VERBOSE_OUTPUT):
			print(" ~ Creating file: ", filename)
		self.fid = open(filename, 'w', encoding="UTF-8", newline='') # using '' to enable universal newlines mode  # See https://docs.python.org/3/library/io.html#io.TextIOWrapper
		return


	def openFile1(self, full_src_file_name):
		if (VERBOSE_OUTPUT):
			print(" ~ Opening file for reading: ", full_src_file_name)
		self.fid = open(full_src_file_name, 'r')
		return
	

	def openFile2(self, src_dir, filename):
		if (VERBOSE_OUTPUT):
			print(" ~ Opening file for reading: ", filename)
		full_src_file_name = os.path.join(src_dir, filename)
		self.fid = open(full_src_file_name, 'r')
		return


	def appendFile4(self, full_src_file_name):
		if (VERBOSE_OUTPUT):
			print(" ~ Opening file for appending: ", full_src_file_name)
		self.fid = open(full_src_file_name, 'a', encoding="UTF-8", newline='')
		return

	
	def appendFile2(self, src_dir, filename):
		if (VERBOSE_OUTPUT):
			print(" ~ Opening file for appending: ", filename)
		full_src_file_name = os.path.join(src_dir, filename)
		fid = open(full_src_file_name, 'a')
		return fid


	def appendFile3(self, src_dir, filename):
		if (VERBOSE_OUTPUT):
			print(" ~ Opening file for appending: ", filename)
		full_src_file_name = os.path.join(src_dir, filename)
		self.fid = open(full_src_file_name, 'a', encoding="UTF-8", newline='')
		return


	def __appendFile(self):
		if (VERBOSE_OUTPUT):
			print(" ~ Opening file for appending: ", filename)
		self.fid = open(self.full_src_file_name, 'a', encoding="UTF-8", newline='')
		return


	def appendFileAndAddFileHeader(self, src_dir, filename, file_header_str):
		if (VERBOSE_OUTPUT):
			print(" ~ Opening file for appending: ", filename)

		self.full_src_file_name = os.path.join(src_dir, filename)
	# Determine if file exists
		file_exists = self.fileExists(self.full_src_file_name)
		self.fid = open(self.full_src_file_name, 'a', encoding="UTF-8", newline='')
		if not(file_exists):
		# Then open the file and add the file header
			self.writeStrToFile(file_header_str)
	# New. Close the file
		self.closeFile()
		return


	def readFile(self):
		if (VERBOSE_OUTPUT):
			print(" ~ Reading file ...")
		#read_data = fid.read()
		read_data = self.fid.readlines()
		return read_data

	def writeStrToFile(self, string):
		if (VERBOSE_OUTPUT):
			print(" ~ Writing string to file:")
			print(string)
			string = string.replace('\n\r','')
			string = string.replace('\n','')
		
		self.__appendFile()  
		self.fid.write("%s\n" % string)
		self.closeFile()
		return


	def originalWriteStrToFile(self, string):
		if (VERBOSE_OUTPUT):
			print(" ~ Writing string to file:")
			print(string)
			string = string.replace('\n\r','')
			string = string.replace('\n','')
		  
		self.fid.write("%s\n" % string)
		return


	def writeByteStrToFile(self, byte_string):
		if (VERBOSE_OUTPUT):
			print(" ~ Writing byte string to file:")

		print(" ~ byte_string is:")
		print(byte_string)
		string = self.decodeBytesToString(byte_string)
		self.writeStrToFile(string)
		return

## Not exactly what it does, but something will be needed eventualy
##	def readByteStrFromFile(self, byte_string):
##		if (VERBOSE_OUTPUT):
##			print(" ~ Reading byte string from file:")
##		string = self.convertBytesToString(byte_string)
##		writeStrToFile(string)
##		return

	
	def convertStringToBytes(self, string):
		byte_string = bytes(string, 'UTF-8')
		return byte_string


	def convertBytesToString(self, byte_string):
		string = str(byte_string, 'UTF-8')
		return string


	def decodeBytesToString(self, byte_string):
		string = byte_string.decode('UTF-8')
		return string
	

	def closeFile(self):
		if (VERBOSE_OUTPUT):
			print(" ~ Closing File ...")
		
		if (self.fid != None):
			self.fid.close()
	
			# Clear the Fid value
			self.fid = None

		return


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

	
	def fileExists(self, file_path):
		if (VERBOSE_OUTPUT):
			print(" ~ Determining if file exists ...")
		return os.path.isfile(file_path) 
	  

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


	def getFilesInDir(self, import_file_path):
 
		files = [f for f in listdir(import_file_path) if isfile(join(import_file_path, f))]

		print(" ~ Files in Directory: %s" % import_file_path)

		if (len(files) == 0):
			print("   0 files, Empty directory")
			
		for file in files:
			print(file)

		return files
	
	
if __name__ == '__main__':

	print("\n ~ Exercising FileIO Class ...")

	dir_basename = r'./'
	dir_folder_name = 'NewFileIO_Test'
	dir_name = join(dir_basename, dir_folder_name)

	fio = FileIO()

	# Determine if the directory exists
	dir_exists = fio.dirExists(dir_name)
	print(" ~ Dir %s exists is: %s" % (dir_name, str(dir_exists)))

	if not(dir_exists):
		# Make the directory
		print(" ~ Creating Dir: %s" % dir_name)
		
		fio.createDirs(dir_name)
	
	# Verify the directory exists
	dir_exists = fio.dirExists(dir_name)
	print(" ~ Dir %s exists is now: %s" % (dir_name, str(dir_exists)))

	# Get the files in the directory
	# Verify the function works for an empty directory
	files = fio.getFilesInDir(dir_name)
	
	# Check to see if a file that does not exist exists
	dir_basename = dir_name
	filename = 'createFile_1.txt'
	full_filename = join(dir_basename, filename)

	file_exists = fio.fileExists(full_filename)
	print(" ~ File %s exists is: %s" % (full_filename, str(file_exists)))
	
	fio.createFile(full_filename)
	print(" ~ File %s Created" % (full_filename))

	fileExists = fio.fileExists(full_filename)
	print(" ~ File %s exists is now: %s" % (full_filename, str(file_exists)))

	#Write a string to the file
	string = "Hello Cool Rover World!"
	fio.writeStrToFile(string)

	string = "You are about to be roverized!"
	fio.writeStrToFile(string)

	# Close the file
	print(" ~ Closing file ...")
	fio.closeFile()

	# Append the file
	print(" ~ Appending %s" % full_filename)
	fio.appendFile1(full_filename)

	# Append string to the file
	string = "I forgot to add this one thing with the full filename."
	fio.writeStrToFile(string)

	# Close the file
	print(" ~ Closing file ...")
	fio.closeFile()

	# Append the file
	print(" ~ Appending %s" % full_filename)
	fio.appendFile1(full_filename)

	# Append string to the file
	string = "And this one other thing with separate path and filename."
	fio.writeStrToFile(string)

	# Close the file
	print(" ~ Closing file ...")
	fio.closeFile()


	if (1):
		# Read back the file
		# Open the file in append mode
		print(" ~ Opening file in append mode: %s" % full_filename)
		#fid = fio.appendFile2(dir_basename, filename)
		fio.openFile2(dir_basename, filename)
	
	# Note: in order to read a file, the file must be opened with read permissions (only)
		print(" ~ Reading file ...")
		data = fio.readFile()

		print(" ~ File Contents:")
		print(data)
		
		# Close the file
		print(" ~ Closing file ...")
		fio.closeFile()

	# Get the fileparts of the filename
	print(" ~ Getting the file parts of the full filename ...")
	fileparts = fio.getFileParts(full_filename)

	print(" ~ File parts are:")
	print(fileparts)

	# Get the pathparts of the filename
	print(" ~ Getting the path parts of the full filename ...")
	pathparts = fio.getPathParts(full_filename)

	print(" ~ Path parts are:")
	print(pathparts)

	# Get the files in the directory
	# Verify the function works for an empty directory
	files = fio.getFilesInDir(dir_name)
	
	if (1):
		# Read back the file
		# Open the file in append mode
		print(" ~ Opening file in append mode: %s" % full_filename)
		#fid = fio.appendFile2(dir_basename, filename)
		fio.openFile2(dir_basename, filename)

		print(" ~ Reading file ...")
		data = fio.readFile()

		print(" ~ File Contents:")
		print(data)
		
		# Close the file
		print(" ~ Closing file ...")
		fio.closeFile()
	
	print("\n ~ Fini! \n\n")