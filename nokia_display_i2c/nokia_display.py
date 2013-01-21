#! /usr/bin/python
# script to send commands to the nokia display over i2c

import smbus, time

class NokiaDisplay:
	def __init__(self, i2cSlaveAddr = 0x19, i2cBusNbr = 0):
		self.i2cSlaveAddr = i2cSlaveAddr
		self.i2c = smbus.SMBus(i2cBusNbr)

#	def changeSlaveAddress(self, newAddr):
#		self.i2c.write_byte(self.i2cSlaveAddr, 0xA1)
#		self.i2c.write_byte(self.i2cSlaveAddr, newAddr)

	def ClearDisplay(self): # sets all pixels to white
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB0)

	def UpdateDisplay(self): # send buffer to the LCD
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB1)

	def SetContrast(self, val): # adjust the contrast. max is 0x7F
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB2)
		self.i2c.write_byte(self.i2cSlaveAddr, val)

	def TextOut(self, xpos, ypos, text, big = False): # write text at a given position
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB3)
		self.i2c.write_byte(self.i2cSlaveAddr, xpos)
		self.i2c.write_byte(self.i2cSlaveAddr, ypos)
		self.i2c.write_byte(self.i2cSlaveAddr, 1 if big == True else 0)
		self.i2c.write_byte(self.i2cSlaveAddr, len(text))
		for i in range(len(text)):
			self.i2c.write_byte(self.i2cSlaveAddr, ord(text[i]))

	def SetPixel(self, xpos, ypos, val = 1): # set a single pixel : 0:white  1:black  2:xor
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB4)
		self.i2c.write_byte(self.i2cSlaveAddr, xpos)
		self.i2c.write_byte(self.i2cSlaveAddr, ypos)
		self.i2c.write_byte(self.i2cSlaveAddr, val)

	def LineOut(self, x1, y1, x2, y2, val = 1): # set a single pixel : 0:white  1:black  2:xor
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB5)
		self.i2c.write_byte(self.i2cSlaveAddr, x1)
		self.i2c.write_byte(self.i2cSlaveAddr, y1)
		self.i2c.write_byte(self.i2cSlaveAddr, x2)
		self.i2c.write_byte(self.i2cSlaveAddr, y2)
		self.i2c.write_byte(self.i2cSlaveAddr, val)

	def __repr__(self):
		print "atmega interfacing a nokia display at i2c address %d" % self.i2cSlaveAddr



# Main program
if __name__ == "__main__":
	disp = NokiaDisplay(0x13, 1) # bus is 0 on the alix, and 1 on the raspberrypi
	disp.ClearDisplay()
	disp.LineOut(5, 5, 70, 20, 1)
	disp.TextOut(5, 5, "Hello World")
	disp.UpdateDisplay()
	


