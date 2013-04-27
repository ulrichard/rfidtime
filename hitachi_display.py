#! /usr/bin/python
# script to send commands to the hitachi display over i2c

import smbus, time

class HitachiDisplay:
	def __init__(self, i2cSlaveAddr = 0x19, i2cBusNbr = 0):
		self.i2cSlaveAddr = i2cSlaveAddr
		self.i2c = smbus.SMBus(i2cBusNbr)

#	def changeSlaveAddress(self, newAddr):
#		self.i2c.write_byte(self.i2cSlaveAddr, 0xA1)
#		self.i2c.write_byte(self.i2cSlaveAddr, newAddr)

	def ClearDisplay(self): # sets all pixels to white
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB0)
		time.sleep(0.02) # give the micro processor some time to swallow the data

	def SetCursor(self, col, row): # position the cursor col [0, 1] row [0, 15]
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB1)
		self.i2c.write_byte(self.i2cSlaveAddr, col)
		self.i2c.write_byte(self.i2cSlaveAddr, row)
		time.sleep(0.05) # give the micro processor some time to swallow the data

	def Print(self, text): # print text at the current cursor position
		data = [len(text)]
		for i in range(len(text)):
			data.append(ord(text[i]))
		self.i2c.write_i2c_block_data(self.i2cSlaveAddr, 0xB2, data)
		time.sleep(0.05) # give the micro processor some time to swallow the data

	def __repr__(self):
		print "atmega interfacing a hitachi display at i2c address %d" % self.i2cSlaveAddr

# test code
if __name__ == "__main__":
	disp = HitachiDisplay(0x21, 1) # bus is 0 on the alix, and 1 on the raspberrypi
	disp.ClearDisplay()
	disp.SetCursor(5, 1)
	disp.Print("welcome")


