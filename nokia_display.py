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
		data = [xpos, ypos, 1 if big == True else 0, len(text)]
		for i in range(len(text)):
			data.append(ord(text[i]))
		self.i2c.write_i2c_block_data(self.i2cSlaveAddr, 0xB3, data)
		time.sleep(0.01) # give the micro processor some time to swallow the data

	def SetPixel(self, xpos, ypos, val = 1): # set a single pixel : 0:white  1:black  2:xor
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB4)
		self.i2c.write_byte(self.i2cSlaveAddr, xpos)
		self.i2c.write_byte(self.i2cSlaveAddr, ypos)
		self.i2c.write_byte(self.i2cSlaveAddr, val)

	def LineOut(self, x1, y1, x2, y2, val = 1): # draw a line -> val : 0:white  1:black  2:xor
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB5)
		self.i2c.write_byte(self.i2cSlaveAddr, x1)
		self.i2c.write_byte(self.i2cSlaveAddr, y1)
		self.i2c.write_byte(self.i2cSlaveAddr, x2)
		self.i2c.write_byte(self.i2cSlaveAddr, y2)
		self.i2c.write_byte(self.i2cSlaveAddr, val)
		time.sleep(0.005) # give the micro processor some time to swallow the data

	def StartScreen(self):                     # show the start screen
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB6)
		time.sleep(0.02) # give the micro processor some time to swallow the data

	def Backlight(self, Enable): # draw a line -> val : 0:white  1:black  2:xor
		if Enable:
			self.i2c.write_byte(self.i2cSlaveAddr, 0xC1)
		else:
			self.i2c.write_byte(self.i2cSlaveAddr, 0xC2)

	def LedRed(self, val): # set the brightness of the red LED -> 0-255
		self.i2c.write_byte(self.i2cSlaveAddr, 0xC3)
		self.i2c.write_byte(self.i2cSlaveAddr, val)

	def LedGreen(self, val): # set the brightness of the green LED -> 0-255
		self.i2c.write_byte(self.i2cSlaveAddr, 0xC4)
		self.i2c.write_byte(self.i2cSlaveAddr, val)

	def LedBlue(self, val): # set the brightness of the blue LED -> 0-255
		self.i2c.write_byte(self.i2cSlaveAddr, 0xC5)
		self.i2c.write_byte(self.i2cSlaveAddr, val)

	def PlayTone(self, frequency, duration): # play a tone on the piezzo buzzer
		data = [frequency, duration]
		self.i2c.write_i2c_block_data(self.i2cSlaveAddr, 0xCA, data)

	def __repr__(self):
		print "atmega interfacing a nokia display at i2c address %d" % self.i2cSlaveAddr



# test code
if __name__ == "__main__":
	disp = NokiaDisplay(0x19, 1) # bus is 0 on the alix, and 1 on the raspbe
	disp.Backlight(True)
	disp.LedBlue(200)
	disp.ClearDisplay()
	disp.UpdateDisplay()
	time.sleep(1.0)
	disp.LedBlue(0)
	disp.StartScreen()
	disp.UpdateDisplay()
	time.sleep(1.0)
	disp.ClearDisplay()
	disp.UpdateDisplay()
	disp.SetContrast(0x40)
	disp.LineOut(5, 5, 40, 20, 1)
	disp.TextOut(2, 2, "Hello World")
	disp.UpdateDisplay()
	time.sleep(0.2)
	disp.Backlight(False)	


