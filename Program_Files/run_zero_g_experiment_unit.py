import RPi.GPIO as GPIO
import os
from os.path import join

import board
import busio
import time
import datetime

import adafruit_bno055
#import adafruit_ds1307
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import logging
import sys

import threading

from FileIO import *
#from FileHandler import *
from VideoHandler import *
from LcdHandler import *
from JsonFileIO import *

RED_LED_PIN = 15
GREEN_LED_PIN = 14
REC_SWITCH_INPUT_PIN = 0
REC_CONTROL_INPUT_PIN = 4
REC_SENSE_INPUT_PIN = 27

SENSOR_CAL_INDEX = 0
GYRO_CAL_INDEX = 1
ACCEL_CAL_INDEX = 2
MAG_CAL_INDEX = 3

HIGH_VALUE = 1
LOW_VALUE = 0

ADC_ADDRESS = 0x48

RECORD_STATE_SW_VALUE = HIGH_VALUE
STANDBY_STATE_SW_VALUE = LOW_VALUE

INIT_MODE = 0
STANDBY_MODE = 1
RECORD_MODE = 2

VERBOSE_MODE = False


IS_EXP_UNIT = 0
IS_AUX_SENSOR_UNIT = 0
IS_EXP_AND_AUX_SUPERSET_UNIT = 1

TELEMETRY_FILE_HEADER = "Date [yyyy-dd-mm],Time [HH:MM:SS.SS],Temp [deg C],Humidity [%],Pressure [hPa],Altitude [m],Quaternion Quality [unitless], Quaternion_i [unitless],Quaternion_j [unitless],Quaternion_k [unitless],Quaternion_w [unitless],Gyro Quality [unitless],Gyro_x [rad/sec],Gyro_y [rad/sec] ,Gyro_z [rad/sec], Accelerometer Quality [unitless],Accel_x [rad/sec^2],Accel_y [rad/sec^2], Accel_z [rad/sec^2],G_x [rad/sec^2],G_y [rad/sec^2],G_z [rad/sec^2],Magnetometer Quality [unitless],M_x [Teslas],M_y [Teslas],M_z [Teslas]"
ACTION_FILE_HEADER = "Date [yyyy-dd-mm],Time [HH:MM:SS.SS],Action"
BATTERY_TELEMETRY_FILE_HEADER = "Date [yyyy-dd-mm],Time [HH:MM:SS.SS],Battery Voltage [V],Battery Level [%]"

RECORD_TELEMETRY_DELTA_T_IN_SEC = 0.5


#TEMP_TLM = 24.5
#HUMIDITY_TLM = 34.5
#PRESSURE_TLM = 996.8
#ALTITUDE_TLM = 101.62
#QUATERNION_QUALITY_TLM = 2
#QUATERNION_TLM = (0.5, 0.5, 0.5, 0.5)
#GYRO_QUALITY_TLM = 3
#GYRO_TLM = (0.22, 0.33, 0.44)
#ACCEL_QUALITY_TLM = 2
#ACCEL_TLM = "(0.1, 0.7, 0.2)"
#GRAVITY_TLM = (0.8, 0.1, 0.1)
#MAGNETOMETER_QUALITY_TLM = 1
#MAGNETOMETER_TLM = (0.33, 0.33, 0.33)


class ZeroGUnit():
	def __init__(self, is_exp_unit):
		if (VERBOSE_MODE):
			print(" ~ Constructing Zero G Unit Object ...")

		self.is_exp_unit = is_exp_unit
		self.TlmFileIo = FileIO()
		self.BattFileIo = FileIO()
		self.ActFileIo = FileIO()
		self.JsonFileIo = JsonFileIO()

		self.data_output_base_dir = "/home/zerog/Zero_G_Payload/Unit_Output_Data"
		self.data_output_dir = os.path.join(self.data_output_base_dir, "Data")
		self.video_output_dir = os.path.join(self.data_output_base_dir, "Video")
		self.bno055_cal_file_dir = "/home/zerog/Zero_G_Payload/Sensor_Calibration_Data"
		self.bno055_cal_filename = "BNO055_Calibration_File.json"
		self.VH = VideoHandler(self.video_output_dir)
		self.VH.print()
		self.LH = LcdHandler()

		self.printUnitIdentity()


	def print(self):
		if (VERBOSE_MODE):
			print(" ~ Printing Zero G Unit Object ...")
		
		self.printUnitIdentity()

		print("     Is Exp. Unit is: {}".format(self.is_exp_unit))
		print("     Current Mode is: {}".format(self.current_mode))
		print("     Data Output Dir is: {}".format(self.data_output_dir))
		print("     Video Output Dir is: {}".format(self.video_output_dir))
		
		return


	def printUnitIdentity(self):
		if (IS_EXP_UNIT):
			print(" ~ Note: This unit is being run as an EXPERIMENT UNIT ...")
		elif (IS_AUX_SENSOR_UNIT):
			print(" ~ Note: This unit is being run as an AUXILIARY SENSOR UNIT ...")
		elif (IS_EXP_AND_AUX_SUPERSET_UNIT):
			print(" ~ Note: This unit is being run as an EXPERIMENT AND AUXILIARY SENSOR SUPERSET UNIT ...")
		else:
			print(" ~ Error: Invalid Unit Identity type encountered ...")
		return


	def __transitionToInitMode(self):
		if (VERBOSE_MODE):
			print(" ~ Transitioning to Init Mode ...")
		self.current_mode = INIT_MODE

		self.__initializeSystem()

		self.__loadBno055CalData()

		# Get the current date & Time
		current_time = self.__getFormattedRtcTime(":")
		self.current_date = self.__getFormattedRtcDate("-")

		#print(" ~ In __transitionToInitMode, self.current_date is: " + str(self.current_date))

		# Start SPI devices
		self.LH.startLcdDisplay()

		# Create output directories
		self.__createOutputDirs()
		
		# Start Action Logging
		self.__startActionLogging()

		# Log to the action file that the system was initialized
		self.__logAction(current_time, "Transitioned to Init Mode")

		# Start Battery Telemetry recording
		self.__startBatteryTelemetryRecording()
		
		# Record the current battery telemetry
		self.__recordBatteryTelemetry(current_time)


		return


	def __transitionToStandbyMode(self):
		if (VERBOSE_MODE):
			print(" ~ Transitioning to Standby Mode ...")
		self.current_mode = STANDBY_MODE

		# Get the current RTC time
		current_time = self.__getFormattedRtcTime(":")
		#print(" ~ In __transitionToStandbyMode, current_time is: " + str(current_time))

		# Log to the action file change in mode
		self.__logAction(current_time, "Transitioned to Standby Mode")

		# Record the current battery telemetry
		self.__recordBatteryTelemetry(current_time)

		# Turn green LED on and red LED off
		self.__setLedState(GREEN_LED_PIN, HIGH_VALUE)
		self.__setLedState(RED_LED_PIN, LOW_VALUE)

		self.__updateLcdDisplay()

		# Stop video recording
		self.__stopVideoRecording()

		return
		

	def __transitionToRecordMode(self, current_time_struct):
		if (VERBOSE_MODE):
			print(" ~ Transitioning to Record Mode ...")

		self.current_mode = RECORD_MODE

		# Get the current RTC time
		current_time = self.__getFormattedRtcTime(":")
		#print(" ~ In __transitionToStandbyMode, current_time is: " + str(current_time))

		# Log to the action file change in mode
		self.__logAction(current_time, "Transitioned to Record Mode")

		# Record the current battery telemetry
		self.__recordBatteryTelemetry(current_time)

		# Turn green LED off and red LED on
		self.__setLedState(GREEN_LED_PIN, LOW_VALUE)
		self.__setLedState(RED_LED_PIN, HIGH_VALUE)

		self.__updateLcdDisplay()
		
		# Start video recording
		self.__startVideoRecording(current_time_struct)
		
		return


	def __initializeSystem(self):
		if (VERBOSE_MODE):
			print(" ~ Initializing System ...")

		# Set output mode
		GPIO.setmode(GPIO.BCM)
		
		# Set pin directions
		# Inputs
		# Enable R Pi pulldowns on inputs

		# Determine which rec input source to use 
		self.__enableRecInputSource()

		# Outputs
		GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
		GPIO.setup(RED_LED_PIN, GPIO.OUT)

		# Initialize outputs
		GPIO.output(GREEN_LED_PIN, GPIO.LOW)
		GPIO.output(RED_LED_PIN, GPIO.LOW)

		# Start I2C devices
		self.__startI2cDevices()

		return


	def __enableRecInputSource(self):
		if (VERBOSE_MODE):
			print(" ~ Enabling Rec Input Source ...")

		# For Aux unit, will not want to do this:
		if (IS_EXP_UNIT | IS_EXP_AND_AUX_SUPERSET_UNIT):
			# Enable the sense input pin
			GPIO.setup(REC_SENSE_INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
			# Get the sense input pin state to determine the source to enable
			sense_state = self.__getVideoRecordSenseState()
			
			#print(" -> getVideoRecordSenseState is: " + str(sense_state))

			if (sense_state == HIGH_VALUE):
				if (VERBOSE_MODE):
					print(" ~ Enabling Rec Switch as Input Source ...")
				# Then since internal pullups are enabled, the unit is not attached to the payload enclosure
				# As a result, enable the record switch
				GPIO.setup(REC_SWITCH_INPUT_PIN, GPIO.IN) # Note no pud needed here
				self.rec_control_input_pin_enabled = False
			else:
				# The unit is attached to the payload enclosure, so enable the rec control input pin
				if (VERBOSE_MODE):
					print(" ~ Enabling Rec Control Input Pin as Input Source ...")
				GPIO.setup(REC_CONTROL_INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
				self.rec_control_input_pin_enabled = True

			#print(" -> rec_control_input_pin_enabled is: " + str(self.rec_control_input_pin_enabled))
                
		else:
			# Is Aux Sensor Unit
			if (VERBOSE_MODE):
				print(" ~ Enabling Rec Control Input Pin as Input Source ...")
			GPIO.setup(REC_CONTROL_INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
			self.rec_control_input_pin_enabled = True

		return


	def __createOutputDirs(self):
		if (VERBOSE_MODE):
			print(" ~ Creating Output Dirs ...")

		self.TlmFileIo.createDirs(self.data_output_dir)
		self.TlmFileIo.createDirs(self.video_output_dir)

		return


	def __loadBno055CalData(self):
		if (VERBOSE_MODE):
			print(" ~ Loading BNO055 Cal Data ...")

		cal_data = self.JsonFileIo.readJsonFile(self.bno055_cal_file_dir, self.bno055_cal_filename)

		# Assign the cal data values
		self.bno055.Offsets_Magnetometer = cal_data["Offsets_Magnetometer"]
		self.bno055.Offsets_Gyroscope = cal_data["Offsets_Gyroscope"]
		self.bno055.Offsets_Accelerometer = cal_data["Offsets_Accelerometer"]

		
		if (VERBOSE_MODE):
			print(" ~ BNO055 Cal Data Loaded!")
		
		return


	def __generateTelemetryFileName(self):
		if (VERBOSE_MODE):
			print(" ~ Generating Data File Name ...")

		formatted_date = self.__getFormattedRtcDate()
		
		if (IS_EXP_UNIT | IS_EXP_AND_AUX_SUPERSET_UNIT):
			file_basename = "Experiment_Unit_Telemetry_"
		else:
			# Is Aux Unit
			file_basename = "Aux_Sensor_Unit_Telemetry_"

		data_file_name = file_basename + str(formatted_date) + ".csv"

		return data_file_name


	def __startVideoRecording(self, current_time):
		if (VERBOSE_MODE):
			print(" ~ Starting Video Recording ...")

		self.VH.startRecording(current_time)

		#if (VERBOSE_MODE):
		#	print(" ~ Video file name is: " + str(video_file_name))

		return


	def __stopVideoRecording(self):
		if (VERBOSE_MODE):
			print(" ~ Stopping Video Recording ...")
		self.VH.stopRecording()

		return


	def __startDataRecording(self):
		if (VERBOSE_MODE):
			print(" ~ Starting Data Recording ...")
		
		data_file_name = self.__generateTelemetryFileName()
		self.TlmFileIo.appendFileAndAddFileHeader(self.data_output_dir, data_file_name, TELEMETRY_FILE_HEADER)

		if (1):
			print(" ~ Data file name is: " + str(data_file_name))

		return data_file_name


	#def __stopDataRecording(self):
	#	if (VERBOSE_MODE):
	#		print(" ~ Stopping Data Recording ...")
	#	return


	def __generateBatteryTelemetryFileName(self):
		if (VERBOSE_MODE):
			print(" ~ Generating Battery Telemetry File Name ...")

		formatted_date = self.__getFormattedRtcDate()
		
		data_file_name = "Aux_Sensor_Unit_Battery_Telemetry_" + str(formatted_date) + ".csv"

		return data_file_name


	def __recordBatteryTelemetry(self, time):
		if (VERBOSE_MODE):
			print(" ~ Recording Battery Telemetry ...")
		
		read_batt_volts = self.__getBatteryTelemetry()

		if (VERBOSE_MODE):
			print(" ~ Read Battery Voltage is: " + str(read_batt_volts))

		actual_batt_volts = 1.0 * read_batt_volts
		batt_percent = 100.0

		#print(" ~ self.current_date is: " + str(self.current_date))

		tlm_str = "%s,%s,%1.2f,%1.2f" % (self.current_date, time, actual_batt_volts, batt_percent)
		#print(" ~ tlm_str is: " + str(tlm_str))

		self.BattFileIo.writeStrToFile(tlm_str)

		if (VERBOSE_MODE):
			print(" ~ Battery Telemetry is: " + str(tlm_str))

		return


	def __generateActionFileName(self):
		if (VERBOSE_MODE):
			print(" ~ Generating Action File Name ...")

		formatted_date = self.__getFormattedRtcDate()
		
		if (IS_EXP_UNIT):
			file_basename = "Experiment_Unit_Action_Log_"
		else:
			# Is Aux Unit
			file_basename = "Aux_Sensor_Unit_Action_Log_"

		data_file_name = file_basename + str(formatted_date) + ".csv"

		return data_file_name


	def __logAction(self, time, action):
		if (VERBOSE_MODE):
			print(" ~ Logging Action ...")
		
		act_str = "%s,%s,%s" % (self.current_date, time, action)

		if (1):
			print(" ~ Action Logged is: " + str(act_str))

		self.ActFileIo.writeStrToFile(act_str)

		return


	def __startActionLogging(self):
		if (VERBOSE_MODE):
			print(" ~ Starting Action Logging ...")

		act_log_file_name = self.__generateActionFileName()
		self.ActFileIo.appendFileAndAddFileHeader(self.data_output_dir, act_log_file_name, ACTION_FILE_HEADER)

		if (1):
			print(" ~ Data file name is: " + str(act_log_file_name))

		return act_log_file_name

		return


	def __startBatteryTelemetryRecording(self):
		if (VERBOSE_MODE):
			print(" ~ Starting Battery Telemetry Recording ...")

		data_file_name = self.__generateBatteryTelemetryFileName()
		self.BattFileIo.appendFileAndAddFileHeader(self.data_output_dir, data_file_name, BATTERY_TELEMETRY_FILE_HEADER)

		if (1):
			print(" ~ Data file name is: " + str(data_file_name))

		return


	def __getVideoRecordSenseState(self):
		if (VERBOSE_MODE):
			print(" ~ Getting Video Record Sense State ...")
		# Since internal pullups are enabled, if the state is high, then the board is not plugged into the experiment enclosure
		
		sense_state = GPIO.input(REC_SENSE_INPUT_PIN)

		if (VERBOSE_MODE):
			print(" ~ Record Sense State is: %d" % sense_state)

		return sense_state


	def __getVideoRecordInputState(self):
		if (VERBOSE_MODE):
			print(" ~ Getting Video Record Input State ...")

		#print(" -> In __getVideoRecordInputState, rec_control_input_pin_enabled is: " + str(self.rec_control_input_pin_enabled))

		if (self.rec_control_input_pin_enabled):
			sw_state = self.__getVideoRecordInputState()
		else:
			sw_state = self.__getVideoRecordSwitchState()

		return sw_state


	def __getVideoRecordSwitchState(self):
		if (VERBOSE_MODE):
			print(" ~ Getting Video Record Switch State ...")

		sw_state = GPIO.input(REC_SWITCH_INPUT_PIN)
		return sw_state


# Duplicate function
#	def __getVideoRecordInputState(self):
#		if (VERBOSE_MODE):
#			print(" ~ Getting Video Record Input State ...")
#		
#		input_state = GPIO.input(REC_CONTROL_INPUT_PIN)
#
#		return input_state


	#def __initSystemTime(self):
	#	if (VERBOSE_MODE):
	#		print(" ~ Initializing System Time ...")
	#	return



	def __setLedState(self, pin_num, state):
		if (VERBOSE_MODE):
			print(" ~ Setting LED State ...")

		GPIO.output(pin_num, state)
		return


	#def __displayMessage(self):
	#	if (VERBOSE_MODE):
	#		print(" ~ Displaying Message ...")
	#	return


	def startUnit(self):
		if (VERBOSE_MODE):
			print(" ~ Starting Unit ...")
		
		#try:
		#	print(" ~ Trying the try ...")
		self.__runUnit()
		#except KeyboardInterrupt:
		#	print(" ~ A keyboard Interrupt was encountered, so exiting and cleaning up ... ")
		#except:		
		#	print(" ~ Houston we have a problem, so alert the user ...")
		#	#self.__blinkLedsError()
		#else: 
		#	print(" ~ Everything worked great!")

		#finally:


	def stopUnit(self):
		if (VERBOSE_MODE):
			print(" ~ Stopping Unit & Cleaning up ...")

		# Log to the action file that the system encountered an error
		current_time = self.__getFormattedRtcTime(":")
		self.__logAction(current_time, "Stopping unit and cleaning up")

		# Stop recording, if recording
		if (self.current_mode == RECORD_MODE):
			self.VH.stopRecording
		
		# Close all files
		self.TlmFileIo.closeFile()
		self.BattFileIo.closeFile()
		self.ActFileIo.closeFile()
		
		# Exit the Display
		self.LH.stopLcdDisplay()
		# OR Display an Error message


	def blinkLedsError(self):
		if (VERBOSE_MODE):
			print(" ~ Blinking Error LEDs ...")

		# Log to the action file that the system encountered an error
		current_time = self.__getFormattedRtcTime(":")
		self.__logAction(current_time, "Unit encountered an error and start blinking Error LEDs")

		# Then stop the unit
		self.stopUnit()

		# Turn green LED off and red LED on
		while(1):
			self.__setLedState(GREEN_LED_PIN, LOW_VALUE)
			self.__setLedState(RED_LED_PIN, LOW_VALUE)
			time.sleep(1)
			self.__setLedState(GREEN_LED_PIN, HIGH_VALUE)
			self.__setLedState(RED_LED_PIN, HIGH_VALUE)
			time.sleep(1)


	def __runUnit(self):
		if (VERBOSE_MODE):
			print(" ~ Running Unit ...")
		
		# Initialize system
		self.__transitionToInitMode()

		# Start data recording
		self.__startDataRecording()

		# Then automatically transition into Standby mode
		self.__transitionToStandbyMode()

		while (1):
			if (1):			
				self.__performModeIteration()
				time.sleep(RECORD_TELEMETRY_DELTA_T_IN_SEC)
			else:
				# This does not work reliably since camera uses threading
				self.__call_repeatedly_with_delta_time(RECORD_TELEMETRY_DELTA_T_IN_SEC, self.__performModeIteration)
		
		return


	def __call_repeatedly_with_delta_time(self, interval, function_to_call):
		def infinite_loop():
			threading.Timer(interval, infinite_loop).start()
			function_to_call()
		infinite_loop()


	def __performModeIteration(self):
		if (VERBOSE_MODE):
			print(" ~ Performing Mode Iteration ...")

		self.__performSensorTelemetryIteration()

		# Update the Video Handler
		# Really only needs to be updated when in record mode

		if (self.current_mode == RECORD_MODE):
			# Get RTC Time
			current_time_struct = self.getRtcTimeStruct()

			self.VH.updateTimeStruct(current_time_struct)

		# Get the Record switch input state
		rec_sw_state = self.__getVideoRecordInputState()
		if ((self.current_mode == STANDBY_MODE) and (rec_sw_state == RECORD_STATE_SW_VALUE)):
			# Then transition to record mode
			current_time_struct = self.getRtcTimeStruct()
			self.__transitionToRecordMode(current_time_struct)
		elif ((self.current_mode == RECORD_MODE) and (rec_sw_state == STANDBY_STATE_SW_VALUE)):
			# Then transition to Standby mode
			self.__transitionToStandbyMode()
		else:
			if (VERBOSE_MODE):
				print(" ~ Current mode is: " + str(self.current_mode) + " and rec_sw_state is: " + str(rec_sw_state))
			
			self.__updateLcdDisplay()

		return


	def __updateLcdDisplay(self):
		if (VERBOSE_MODE):
			print(" ~ Updating LCD Display ...")

		current_time = self.__getFormattedRtcTime(":", False)
		
		if (0):
			batt_volts = self.__getBatteryTelemetry()
			batt_percent = 100
		else:
			batt_volts = 5.0
			batt_percent = 100

		self.LH.updateLcdDisplay(current_time, self.current_date, self.current_mode, batt_volts, batt_percent)

		return


	def __performSensorTelemetryIteration(self):

		for iteration in range(20):
			if (VERBOSE_MODE):
				print(" ~ Get Sensor Telemetry iteration is: " + str(iteration))

			# Get Sensor Telemetry
			exec_status, sensor_tlm_str = self.__getSensorTelemetry()
			
			if (exec_status == 0):
				# Write sensor telemetry to file
				self.TlmFileIo.writeStrToFile(sensor_tlm_str)
				break
			
			if (iteration == 20-1):
				print(" ~ WARNING: No good Sensor TLM in MAX Iterations ...")


	def __getSensorTelemetry(self):
		if (VERBOSE_MODE):
			print(" ~ Getting Sensor Telemetry ...")

		date_tlm = self.__getFormattedRtcDate("-")
		#date_tlm = date_tlm.replace("_", "-")

		time_tlm = self.__getFormattedRtcTime(":")
		#time_tlm = time_tlm.replace("_", ":")

		try:
			self.__getBme280Telemetry()
			self.__getBno055Telemetry()

			tlm_mixed_list = [date_tlm, time_tlm, self.bme280_temp_tlm, self.bme280_rh_tlm, self.bme280_pres_tlm, self.bme280_alt_tlm, self.bno055_cal_status[SENSOR_CAL_INDEX], self.bno055_quat_tlm, self.bno055_cal_status[GYRO_CAL_INDEX], self.bno055_gyro_tlm, self.bno055_cal_status[ACCEL_CAL_INDEX], self.bno055_accel_tlm, self.bno055_g_tlm, self.bno055_cal_status[MAG_CAL_INDEX], self.bno055_mag_tlm]

			tlm_str_list = [str(element) for element in tlm_mixed_list]
			tlm_concatenated_str = ",".join(tlm_str_list)

			# Eliminate parentheses and any other un-needed characters
			tlm_concatenated_str = tlm_concatenated_str.replace("(", "")
			tlm_concatenated_str = tlm_concatenated_str.replace(")", "")
			tlm_concatenated_str = tlm_concatenated_str.replace(" ", "")
	    
			if (VERBOSE_MODE):
				print("   tlm_concatenated_str is: " + tlm_concatenated_str)

		except:
			print(" ~ WARNING: Encountered Exception in __getSensorTelemetry ...")
			return (1, "")
		
		else: 
			return (0, tlm_concatenated_str)

	
	def __startI2cDevices(self):
		if (VERBOSE_MODE):
			print(" ~ Starting I2C Devices ...")

		self.i2c = board.I2C()
		#self.rtc = adafruit_ds1307.DS1307(self.i2c)
		self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c) # Addr 0x77
		self.ads1113 = ADS.ADS1115(self.i2c, address=ADC_ADDRESS, gain=1)
		self.bno055 = adafruit_bno055.BNO055_I2C(self.i2c)
		return


#	def syncRtcTime(self):
#		if (VERBOSE_MODE):
#			print(" ~ Syncing RTC time to current localtime using time ...")
#
#		# First initialize the system to start I2C devices, including the RTC
#		self.__initializeSystem()
#
#		t = time.localtime()
#		self.rtc.datetime = t
#		print(" ~ RTC time sycn'ed!")
#		return
#
#
	def getRtcTimeStruct(self):
		if (VERBOSE_MODE):
			print(" ~ Getting RTC Time Struct ...")
			print(" ~ Current time struct from RTC is: ")
		
		rtc_current_time_struct = datetime.now()

		if (VERBOSE_MODE):
			print(rtc_current_time_struct)

		return rtc_current_time_struct


	def __getFormattedRtcTime(self, delimeter="_", include_ms_field=True):
		if (VERBOSE_MODE):
			print(" ~ Getting Formatted RTC Time ...")

		#if (0):
		#	# When interfacing with the RTC directly
		#	current_time = self.rtc.datetime
		#	formatted_time = ("%d%c%02d%c%02d" % (current_time.tm_hour, delimeter, current_time.tm_min, delimeter, current_time.tm_sec))
		#else:
		# When using the Raspberry Pi time set by the RTC
		current_time = datetime.now()
		if (include_ms_field):
			# Then round the microseconds to the desired number of sig figs. This results in a number that is between 0 and 100, and really only want 0 to 99
			rounded_microsecond = round(current_time.microsecond/10000)
			if (rounded_microsecond == 100):
				rounded_microsecond = 99

			formatted_time = current_time.strftime("%d%c%02d%c%02d.%02d" % (current_time.hour, delimeter, current_time.minute, delimeter, current_time.second, rounded_microsecond))
		else:
			formatted_time = current_time.strftime("%d%c%02d%c%02d" % (current_time.hour, delimeter, current_time.minute, delimeter, current_time.second))

		return formatted_time


	def __getFormattedRtcDate(self, delimeter="_"):
		if (VERBOSE_MODE):
			print(" ~ Getting Formatted RTC Date ...")
		#if (0):
		#	# When interfacing with the RTC directly
		#	current_time = self.rtc.datetime
		#	formatted_date = ("%d%c%d%c%d" % (current_time.tm_year, delimeter, current_time.tm_mon, delimeter, current_time.tm_mday))
		#else:
		# When using the Raspberry Pi time set by the RTC
		current_time = datetime.now()
		formatted_date = ("%d%c%d%c%d" % (current_time.year, delimeter, current_time.month, delimeter, current_time.day))
		#
		return formatted_date


	def __getFormattedRtcDateAndTime(self):
		if (VERBOSE_MODE):
			print(" ~ Getting Formatted Current RTC Date and Time ...")

		delimeter = "_"
		include_ms_field = False
		formatted_date = self.__getFormattedRtcDate(delimeter, include_ms_field)
		formatted_time = self.__getFormattedRtcTime()
		formatted_date_time = formatted_date + "__" + formatted_time
		
		if (VERBOSE_MODE):
			print(" ~ Formatted Current Date Time is: " + str(formatted_date_time)) 

		return formatted_date_time


	def __getBme280Telemetry(self):
		if (VERBOSE_MODE):
			print(" ~ Getting BME280 Telemetry ...")
		self.bme280.sea_level_pressure = 1013.25

		self.bme280_temp_tlm = round(self.bme280.temperature, 1)
		self.bme280_rh_tlm   = round(self.bme280.relative_humidity, 1)
		self.bme280_pres_tlm = round(self.bme280.pressure, 1)
		self.bme280_alt_tlm  = round(self.bme280.altitude, 1)

		return


	def __getBatteryTelemetry(self):
		if (VERBOSE_MODE):
			print(" ~ Getting ADS1113 Battery Telemetry ...")

		chan0 = AnalogIn(self.ads1113, ADS.P0)

		if (VERBOSE_MODE):
			print(" ~ Printing Channel Measurements ...")
			print("   A0: " + str(chan0.value) + " cnts, " + str(chan0.voltage) + " V")
		
		return chan0.voltage


	def __getBno055Telemetry(self):
		if (VERBOSE_MODE):
			print(" ~ Getting BNO055 Telemetry ...")
		self.bno055.set_normal_mode()

		self.bno055_mode_tlm = self.bno055.mode
		self.bno055_quat_tlm = tuple(round(x, 6) for x in self.bno055.quaternion)
		self.bno055_cal_status = self.bno055.calibration_status
		self.bno055_accel_tlm = tuple(round(x, 6) for x in self.bno055.acceleration)
		self.bno055_mag_tlm = tuple(round(x, 3) for x in self.bno055.magnetic)
		self.bno055_g_tlm = tuple(round(x, 6) for x in self.bno055.gravity)
		self.bno055_gyro_tlm = tuple(round(x, 6) for x in self.bno055.gyro)
		self.bno055_linear_accel_tlm = tuple(round(x, 6) for x in self.bno055.linear_acceleration)


	def __loadBno055Offsets(self):
		#bno055.offsets_magnetometer
		#bno055.offsets_accelerometer
		# TBD
		return



	def performSelfTest(self):
		if (1):
			print(" ~ Performing Self Test ...")

		self.__selfTestI2CDevices()

		return


	def __selfTestI2CDevices(self):
		if (1):
			print(" ~ Running Self Test on I2C Devices ...")

		self.i2c = board.I2C()
		rtc_status_code = self.__selfTestRtcI2CDevice()
		bme_status_code = self.__selfTestBme280I2CDevice()
		bno_status_code = self.__selfTestBno055I2CDevice()
		ads_status_code = self.__selfTestAds1113I2CDevice()
		
		return (rtc_status_code, bme_status_code, bno_status_code, ads_status_code)


#	def __selfTestRtcI2CDevice(self):
#		if (1):
#			print(" ~ Running Self Test on RTC I2C Device ...")
#
#		try:
#			self.rtc = adafruit_ds1307.DS1307(self.i2c)
#
#		except:
#			print("   - ERROR: RTC start result: FAILED!")
#			return 1
#
#		else:
#			print("   - RTC start result: PASSED")
#			
#			# Then get the RTC time struct
#			self.getRtcTimeStruct()
#
#			return 0


	def __selfTestBme280I2CDevice(self):
		if (1):
			print(" ~ Running Self Test on BME280 I2C Device ...")

		try:
			self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)

		except:
			print("   - ERROR: BME280 start result: FAILED!")
			return 1

		else:
			print("   - BME280 start result: PASSED")
			
			# Then get the BME280 telemetry
			self.__getBme280Telemetry()

			return 0


	def __selfTestBno055I2CDevice(self):
		if (1):
			print(" ~ Running Self Test on BNO055 I2C Device ...")

		try:
			self.bno055 = adafruit_bno055.BNO055_I2C(self.i2c)

		except:
			print("   - ERROR: BNO055 start result: FAILED!")
			return 1

		else:
			print("   - BNO055 start result: PASSED")
			
			# Then get the BNO055 telemetry
			self.__getBno055Telemetry()

			return 0


	def __selfTestAds1113I2CDevice(self):
		if (1):
			print(" ~ Running Self Test on ADS1113 I2C Device ...")

		try:
			self.ads1113 = ADS.ADS1115(self.i2c, address=ADC_ADDRESS, gain=1)

		except:
			print("   - ERROR: ADS1113 start result: FAILED!")
			return 1

		else:
			print("   - ADS1113 start result: PASSED")
			
			# Then get the ADS1113 telemetry
			self.__getBatteryTelemetry()

			return 0

		# # Addr 0x77
		#
		#






print(" ~ Running Zero G Unit ...\n")

zgu = ZeroGUnit(True)
#zgu.syncRtcTime()
#zgu.getRtcTimeStruct()
#zgu.startUnit()
#zgu.print()
#time.sleep(5)

# Syncing the RTC
#zgu.getRtcTimeStruct()

if (0):
	# Sync the RTC's time with the current system time
	zgu.syncRtcTime()

#zgu.getRtcTimeStruct()

try:
	print(" ~ Trying the try ...")
	zgu.startUnit()

except KeyboardInterrupt:
	print(" ~ A keyboard Interrupt was encountered, so exiting and cleaning up... ")
	zgu.stopUnit()

except:
	print(" ~ Houston we have a problem, so alert the user ...")
	zgu.blinkLedsError()
else: 
	print(" ~ Congrats, everything worked great!")

#finally:


print("\n ~ Fini! \n")