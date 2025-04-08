# Wow, all of these imports take a good amount of time
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import time
import os
from os.path import join

VERBOSE_MODE = False

MAX_RECORD_DURATION_IN_SEC = 60 #300
VIDEO_EXT = ".mp4"
NUM_SEC_IN_HR = 60 * 60
NUM_SEC_IN_MIN = 60

class VideoHandler():
	def __init__(self, video_output_dir):
		if (VERBOSE_MODE):
			print(" ~ Constructing Video Handler Object ...")

		self.save_to_dir = video_output_dir
		self.recording_in_progress = False
		self.video_filename = ""
		#self.max_record_duration_reached = False
		self.picamera_started = False
		self.record_start_time = None
		self.current_time = None
		self.record_time_remaining = MAX_RECORD_DURATION_IN_SEC

	def print(self):
		if (VERBOSE_MODE):
			print(" ~ Printing Video Handler Object ...")
		print("   Save to Dir is: " + str(self.save_to_dir))
		print("   Recording in Progress is: " + str(self.recording_in_progress))
		print("   Video Filename is: " + str(self.save_to_dir))
		#print("   Max Record Duration Reached is: " + str(self.max_record_duration_reached))
		print("   Record Start Time is: " + str(self.record_start_time))
		print("   Current Time is: " + str(self.current_time))
		print("   Record Time Remaining is: " + str(self.record_time_remaining))


	def updateTimeStruct(self, time):
		if (VERBOSE_MODE):
			print(" ~ Updating Time ...")
		self.current_time = time

		# Determine the record time remaining
		self.__computeRecordTimeRemaining()

		return


	def startRecording(self, time):
		if (VERBOSE_MODE):
			print(" ~ Start Recording Video ...")
		
		self.current_time = time
		self.record_start_time = self.current_time

		# Construct the recording filename
		self.__constructVideoFilename()

		# Set the recording flag
		self.recording_in_progress = True
		
		# Start the camera
		self.__startCamera()
 
		return
	

	def __constructVideoFilename(self):
		if (VERBOSE_MODE):
			print(" ~ Constructing Video Filename ...")
		
		#print(" -> self.record_start_time is: " + str(self.record_start_time))

		# Construct the video Filename from the self.record_start_time
		#filename = ("Experiment_Unit_Video_%d-%d-%d__%d-%02d-%02d%s" % (self.record_start_time.tm_year, self.record_start_time.tm_mon, self.record_start_time.tm_mday, self.record_start_time.tm_hour, self.record_start_time.tm_min, self.record_start_time.tm_sec, VIDEO_EXT))
		filename = ("Experiment_Unit_Video_%d-%d-%d__%d-%02d-%02d%s" % (self.record_start_time.year, self.record_start_time.month, self.record_start_time.day, self.record_start_time.hour, self.record_start_time.minute, self.record_start_time.second, VIDEO_EXT))

		#print(" ~ filename is: " + filename)

		self.video_filename = os.path.join(self.save_to_dir, filename)

		#print(" ~ self.video_filename is: " + self.video_filename)
		return


	def stopRecording(self):
		if (VERBOSE_MODE):
			print(" ~ Stop Recording Video ...")
		
		# Stop the camera
		self.__stopCamera()

		# Set the recording flag
		self.recording_in_progress = False

		self.record_time_remaining = MAX_RECORD_DURATION_IN_SEC

		return


	def __convertTimeStructToSecs(self, t_struct):
		if (VERBOSE_MODE):
			print(" ~ Converting Time Struct to Seconds ...")
		
		#time_in_sec = t_struct.tm_hour * NUM_SEC_IN_HR + t_struct.tm_min * NUM_SEC_IN_MIN + t_struct.tm_sec
		time_in_sec = t_struct.hour * NUM_SEC_IN_HR + t_struct.minute * NUM_SEC_IN_MIN + t_struct.second
		
		return time_in_sec


	def __subtract(self, t1_struct, t0_struct):
		if (VERBOSE_MODE):
			print(" ~ Computing time structure difference in seconds ...")

		t1_in_sec = self.__convertTimeStructToSecs(t1_struct)
		t0_in_sec = self.__convertTimeStructToSecs(t0_struct)

		delta_in_sec = t1_in_sec - t0_in_sec

		#print(" ~ Delta in Sec is: " + str(delta_in_sec))

		return delta_in_sec


	def __computeRecordTimeRemaining(self):
		if (VERBOSE_MODE):
			print(" ~ Computing Record Time Remaining ...")

		if (self.picamera_started):
			recording_duration_in_sec = self.__subtract(self.current_time, self.record_start_time)
			
			if (recording_duration_in_sec >= MAX_RECORD_DURATION_IN_SEC):
				print(" ~ Maximum Set Recording Time Encountered. Starting new video ...")
				# First stop recording
				self.stopRecording()
				
				#time.sleep(10)

				# Then start a new recording with a new filename			
				self.startRecording(self.current_time)
			else:
				# Compute the time remaining
				self.record_time_remaining = MAX_RECORD_DURATION_IN_SEC - recording_duration_in_sec
				
			#print(" ~ self.record_time_remaining is: " + str(self.record_time_remaining))

		# The else statement below is optional code:
		#else:
			#print(" ~ Camera has not been started yet.  Ignoring Compute cmd.")

		return


	def getRecordTimeRemaining(self):
		if (VERBOSE_MODE):
			print(" ~ Getting Record Time Remaining ...")

		return self.record_time_remaining 


	def __startCamera(self):
		if (VERBOSE_MODE):
			print(" ~ Starting Camera ...")
		
		if not(self.picamera_started):
			self.picam2 = Picamera2()
			self.picamera_started = True

			config = self.picam2.create_video_configuration()
			self.picam2.configure(config)

			#self.picam2.start_preview(Preview.QTGL)

			# Set camera to manual focus at the closest lens position (to the camera)
			self.picam2.set_controls({"AfMode": 0, "LensPosition" : 15})
			
			# Set the desired framerate
			self.picam2.set_controls({"FrameRate": 30})

		self.picam2.start()
		encoder = H264Encoder(bitrate=100000000)

		video_output = FfmpegOutput(self.video_filename)

		#time.sleep(5)

		# Close the preview window
		#self.picam2.stop_preview()

		self.picam2.start_recording(encoder, output=video_output)
	
		return


	def __stopCamera(self):
		if (VERBOSE_MODE):
			print(" ~ Stopping Camera ...")
		
		if (self.picamera_started):
			self.picam2.stop_recording()
			self.picam2.stop()
			
			if (VERBOSE_MODE):
				print(" ~ Recording Finished ...")
		
		# The else statement below is optional code:
		#else:
		#	print(" ~ Camera has not been started yet.  Ignoring Stop cmd.")

		return
