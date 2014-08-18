#! /usr/bin/python3
# script to send commands to the hitachi display over i2c

import time, os, sys
lib_path = os.path.abspath('.')
sys.path.append(lib_path + '/rfid532lib')
#from quick2wire.i2c import I2CMaster, reading, writing
import rfid532lib.quick2wire.i2c as i2c

class HitachiDisplay:
	def __init__(self, i2cSlaveAddr = 0x24, i2cBusNbr = 0):
		self.i2cSlaveAddr = i2cSlaveAddr
		self.i2c = i2c.I2CMaster()

	def ClearDisplay(self): # sets all pixels to white
		self.i2c.transaction(
			i2c.writing_bytes(self.i2cSlaveAddr, 0xB0)
		)
		time.sleep(0.04) # give the micro processor some time to swallow the data

	def SetCursor(self, col, row): # position the cursor col [0, 1] row [0, 15]
		self.i2c.transaction(
			i2c.writing_bytes(self.i2cSlaveAddr, 0xB1, col, row)
		)
		time.sleep(0.08) # give the micro processor some time to swallow the data

	def Print(self, text): # print text at the current cursor position
		data = [0xB2, len(text)]
		for i in range(len(text)):
			data.append(ord(text[i]))
		self.i2c.transaction(
			i2c.writing(self.i2cSlaveAddr, data)
		)
		time.sleep(0.08) # give the micro processor some time to swallow the data

	def __repr__(self):
		print("atmega interfacing a hitachi display at i2c address %d" % self.i2cSlaveAddr)

# test code
if __name__ == "__main__":
	disp = HitachiDisplay(0x21, 1) # bus is 0 on the alix, and 1 on the raspberrypi
	disp.ClearDisplay()
	disp.SetCursor(0, 1)
	disp.Print("welcome python3")


