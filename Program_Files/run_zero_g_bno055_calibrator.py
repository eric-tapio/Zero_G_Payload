# SPDX-FileCopyrightText: 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
# Modified by Eric Tapio for the Zero G program

"""
`zero_g_bno055_calibrator.py`
===============================================================================
A CircuitPython module for calibrating the BNo055 9-DoF sensor. After manually
calibrating the sensor, the module produces calibration offset tuples for use
in project code.

* Author(s): JG for Cedar Grove Maker Studios

Implementation Notes
--------------------
**Hardware:**
* Adafruit BNo055 9-DoF sensor
**Software and Dependencies:**
* Driver library for the sensor in the Adafruit CircuitPython Library Bundle
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

import json
import time
import board
import adafruit_bno055
from JsonFileIO import *

READ_BACK_JSON_FILE = True

# pylint: disable=too-few-public-methods
class Mode:
	CONFIG_MODE = 0x00
	ACCONLY_MODE = 0x01
	MAGONLY_MODE = 0x02
	GYRONLY_MODE = 0x03
	ACCMAG_MODE = 0x04
	ACCGYRO_MODE = 0x05
	MAGGYRO_MODE = 0x06
	AMG_MODE = 0x07
	IMUPLUS_MODE = 0x08
	COMPASS_MODE = 0x09
	M4G_MODE = 0x0A
	NDOF_FMC_OFF_MODE = 0x0B
	NDOF_MODE = 0x0C


# Create a Json File IO object for writing the calibration data
JsonFileIo = JsonFileIO()
bno055_cal_file_dir = "/home/Zero_G_Payload/Sensor_Calibration_Data"
bno055_cal_filename = "BNO055_Calibration_File.json"

# Uncomment these lines for UART interface connection
# uart = board.UART()
# sensor = adafruit_bno055.BNO055_UART(uart)

# Instantiate I2C interface connection
i2c = board.I2C()  # For board.SCL and board.SDA
#i2c = board.STEMMA_I2C()  # For the built-in STEMMA QT connection
sensor = adafruit_bno055.BNO055_I2C(i2c)
sensor.mode = Mode.NDOF_MODE  # Set the sensor to NDOF_MODE

print("\n ~ Performing Zero G BNO055 Sensor Calibration ...")

if (0):
	print("\n ~ BEFORE CALIBRATION:")
	print("Insert these preset offset values into project code:")
	print(f"  Offsets_Magnetometer:  {sensor.offsets_magnetometer}")
	print(f"  Offsets_Gyroscope:	 {sensor.offsets_gyroscope}")
	print(f"  Offsets_Accelerometer: {sensor.offsets_accelerometer}")

print("\n ~ Magnetometer Calibration Step: Step 1 of 3")
print("    Holding the Experiment Unit, rotate it slowly in a figure-eight pattern until calibrated ...")
#print("Magnetometer: Perform the figure-eight calibration dance.")
while not sensor.calibration_status[3] == 3:
	# Calibration Dance Step One: Magnetometer
	#   Move sensor away from magnetic interference or shields
	#   Perform the figure-eight until calibrated
	print(f"Mag Calib Status: {100 / 3 * sensor.calibration_status[3]:3.0f}%")
	time.sleep(1)
print("... CALIBRATED")
time.sleep(1)


print("\n ~ Accelerometer Calibration Step: Step 2 of 3")
print("    Hold the Experiment Unit in each of the six stable positions below for a few seconds each:")
print("    	1) x-axis right, y-axis up,    z-axis away")
print("    	2) x-axis up,	 y-axis left,  z-axis away")
print("    	3) x-axis left,  y-axis down,  z-axis away")
print("    	4) x-axis down,  y-axis right, z-axis away")
print("    	5) x-axis left,  y-axis right, z-axis up")
print("    	6) x-axis right, y-axis left,  z-axis down")
print("    The order of the six stable positions does not matter.")
print("    Repeat the six stable position steps until calibrated ...")


#print("Accelerometer: Perform the six-step calibration dance.")
while not sensor.calibration_status[2] == 3:
	# Calibration Dance Step Two: Accelerometer
	#   Place sensor board into six stable positions for a few seconds each:
	#	1) x-axis right, y-axis up,	z-axis away
	#	2) x-axis up,	y-axis left,  z-axis away
	#	3) x-axis left,  y-axis down,  z-axis away
	#	4) x-axis down,  y-axis right, z-axis away
	#	5) x-axis left,  y-axis right, z-axis up
	#	6) x-axis right, y-axis left,  z-axis down
	#   Repeat the steps until calibrated
	print(f"Accel Calib Status: {100 / 3 * sensor.calibration_status[2]:3.0f}%")
	time.sleep(1)
print("... CALIBRATED")
time.sleep(1)


print("\n ~ Gyroscope Calibration Step: Step 3 of 3")
print("    Hold the Experiment Unit in any of the six stable position for a few seconds:")
print("    Repeat until calibrated ...")

#print("Gyroscope: Perform the hold-in-place calibration dance.")
while not sensor.calibration_status[1] == 3:
	# Calibration Dance Step Three: Gyroscope
	#  Place sensor in any stable position for a few seconds
	#  (Accelerometer calibration may also calibrate the gyro)
	print(f"Gyro Calib Status: {100 / 3 * sensor.calibration_status[1]:3.0f}%")
	time.sleep(1)
print("... CALIBRATED")
time.sleep(1)

print("\n ~ Calibration Complete!\n")

#print("\n ~ AFTER CALIBRATION COMPLETED:")
#print("Insert these preset offset values into project code:")
print("\n ~ Calibration data that will be used during sensor operation:")
print(f"  Offsets_Magnetometer:  {sensor.offsets_magnetometer}")
print(f"  Offsets_Gyroscope:	 {sensor.offsets_gyroscope}")
print(f"  Offsets_Accelerometer: {sensor.offsets_accelerometer}")
print("")

# Write the offsets to a Json File
# Construct the JSON Data
data = {
	"Offsets_Magnetometer" : sensor.offsets_magnetometer,
	"Offsets_Gyroscope" : sensor.offsets_gyroscope,
	"Offsets_Accelerometer" : sensor.offsets_accelerometer
}

# Write the JSON data
JsonFileIo.writeJsonFile(bno055_cal_file_dir, bno055_cal_filename, data)

if (READ_BACK_JSON_FILE):
	# Read the saved JSON data
	JsonFileIo.read_data = JsonFileIo.readJsonFile(bno055_cal_file_dir, bno055_cal_filename)

#print("\n\n ~ Fini! \n\n")
