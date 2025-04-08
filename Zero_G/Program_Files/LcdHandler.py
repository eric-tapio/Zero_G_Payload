#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys 
import time
import logging
import spidev as SPI
from datetime import datetime

sys.path.append("..")
from LCD_Module_RPI_code.RaspberryPi.python.lib import LCD_2inch
#from LCD_Module_RPI_code.RaspberryPi.python.lib import LCD_2inch4
from PIL import Image, ImageDraw, ImageFont

LINE_1_DOWN_POS = 2 # DOWN 
LINE_1_RIGHT_POS = 50 # Right
LINE_1_FONT_SIZE = 60

LINE_2_DOWN_POS = 74 # DOWN 
LINE_2_RIGHT_POS = 90 # Right
LINE_2_FONT_SIZE = 30

LINE_3_DOWN_POS = 115 # DOWN 
LINE_3_RIGHT_POS = 5 # Right
LINE_3_FONT_SIZE = 50

LINE_4_DOWN_POS = 180 # DOWN 
LINE_4_RIGHT_POS = 20 # Right
LINE_4_FONT_SIZE = 40

# disp.width = 240
# disp.height = 320

VERBOSE_MODE = False

SHOW_SPLASH_SCREEN = False

INIT_MODE = 0
STANDBY_MODE = 1
RECORD_MODE = 2
ERROR_MODE = 3 # Think about it

class LcdHandler:

    def __init__(self):
        self.fid = None
        
        # Raspberry Pi pin configuration:
        self.RST = 6
        self.DC = 5
        self.BL = 12
        self.bus = 0 
        self.device = 0
        
        self.font1 = ImageFont.truetype("/home/zerog/Zero_G/Program_Files/LCD_Module_RPI_code/RaspberryPi/python/Font/Font02.ttf", LINE_1_FONT_SIZE)
        self.font2 = ImageFont.truetype("/home/zerog/Zero_G/Program_Files/LCD_Module_RPI_code/RaspberryPi/python/Font/Font02.ttf", LINE_2_FONT_SIZE)
        self.font3 = ImageFont.truetype("/home/zerog/Zero_G/Program_Files/LCD_Module_RPI_code/RaspberryPi/python/Font/Font02.ttf", LINE_3_FONT_SIZE)
        self.font4 = ImageFont.truetype("/home/zerog/Zero_G/Program_Files/LCD_Module_RPI_code/RaspberryPi/python/Font/Font02.ttf", LINE_4_FONT_SIZE)
        
        return


    def __getTime(self):
        if (VERBOSE_MODE):
            print(" ~ Getting Time ...")

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(" ~ Current Time is: ", current_time)

        return current_time


    def __getDate(self):
        if (VERBOSE_MODE):
            print(" ~ Getting Date ...")

        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        print(" ~ Current Date is: ", current_date)

        return current_date


    def updateLcdDisplay(self, time_str, date_str, mode_number, battery_v, battery_pcnt):
        if (VERBOSE_MODE):
            print(" ~ Updating LCD Display ...")

        #time_str = self.__getTime()
        #date_str = self.__getDate()

        batt_v = "%1.1f" % battery_v
        batt_p = "%d" % round(battery_pcnt)

        if (mode_number == INIT_MODE):
            mode = "INIT"
        elif (mode_number == STANDBY_MODE):
            mode = "STANDBY"
        elif (mode_number == RECORD_MODE):
            mode = "RECORDING"
        else:
            print(" ~ WARNING: Encountered an invalid mode number: %d" % mode_number)

        self.draw = ImageDraw.Draw(self.background_image)

        self.draw.rectangle([(LINE_1_RIGHT_POS, LINE_1_DOWN_POS),(self.disp.height, LINE_1_DOWN_POS+LINE_1_FONT_SIZE)], fill="BLACK")    
        self.draw.text((LINE_1_RIGHT_POS, LINE_1_DOWN_POS), time_str, fill="YELLOW", font=self.font1)

        self.draw.rectangle([(LINE_2_RIGHT_POS, LINE_2_DOWN_POS),(self.disp.height, LINE_2_DOWN_POS+LINE_2_FONT_SIZE)], fill="BLACK")    
        self.draw.text((LINE_2_RIGHT_POS, LINE_2_DOWN_POS), date_str, fill="YELLOW", font=self.font2)

        self.draw.rectangle([(LINE_3_RIGHT_POS, LINE_3_DOWN_POS),(self.disp.height, LINE_3_DOWN_POS+LINE_3_FONT_SIZE)], fill="BLACK")    
        self.draw.text((LINE_3_RIGHT_POS, LINE_3_DOWN_POS), "Mode: " + str(mode), fill="WHITE", font=self.font3)

        self.draw.rectangle([(LINE_4_RIGHT_POS, LINE_4_DOWN_POS),(self.disp.height, LINE_4_DOWN_POS+LINE_4_FONT_SIZE)], fill="BLACK")    
        self.draw.text((LINE_4_RIGHT_POS, LINE_4_DOWN_POS), "Batt: " + str(batt_v) + "V, " + str(batt_p) + "%", fill="WHITE", font=self.font4)

	# Notice. Display image is to be destroyed in each iteration
        display_image = self.background_image.rotate(180)
        #display_image = self.background_image.rotate(0)
        self.disp.ShowImage(display_image)


    def startLcdDisplay(self):
        if (VERBOSE_MODE):
            print(" ~ Starting LCD Display ...")

        self.spi = SPI.SpiDev(self.bus, self.device)
        self.disp = LCD_2inch.LCD_2inch(spi=self.spi, spi_freq=10000000, rst=self.RST, dc=self.DC, bl=self.BL)
        #self.disp = LCD_2inch4.LCD_2inch4(spi=self.spi, spi_freq=10000000, rst=self.RST, dc=self.DC, bl=self.BL)
    
        # Initialize library
        self.disp.Init()
    
        # Clear display
        self.disp.clear()
    
        #Set the backlight to 100
        self.disp.bl_DutyCycle(50)

        # Show splash screen
        if (SHOW_SPLASH_SCREEN):
            image = Image.open('/home/zerog/Zero_G/Program_Files/LCD_Module_RPI_code/RaspberryPi/python/pic/LCD_2inch.jpg')	
            #image = Image.open('/home/zerog/Zero_G/Program_Files/LCD_Module_RPI_code/RaspberryPi/python/pic/LCD_2inch4.jpg')	
            image = image.rotate(180)
            #image = image.rotate(0)
            self.disp.ShowImage(image)
            time.sleep(2)

        # Create blank image for drawing
        self.background_image = Image.new("RGB", (self.disp.height, self.disp.width), "BLACK") # Try switching these two
        return


    def stopLcdDisplay(self):
        if (VERBOSE_MODE):
            print(" ~ Stopping LCD Display ...")

        self.disp.module_exit()


if __name__ == '__main__':
    try:
        lH = LcdHandler()
        lH.startLcdDisplay()
        time_str = "12:34:56"
        date_str = "2025:10:12"
        mode_number = 1
        battery_v = "5.6" 
        battery_pcnt = "86%"

        for i in range(40):
            lH.updateLcdDisplay(time_str, date_str, mode_number, battery_v, battery_pcnt)
            time.sleep(0.5)
        lH.stopLcdDisplay()

    except IOError as e:
        logging.info(e)    

    except KeyboardInterrupt:
        lH.stopLcdDisplay()
        exit()