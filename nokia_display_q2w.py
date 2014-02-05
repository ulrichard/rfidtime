#! /usr/bin/python3
# script to send commands to the nokia display over i2c

import time, math, os, sys
from PIL import Image
lib_path = os.path.abspath('.')
sys.path.append(lib_path + '/rfid532lib')
from quick2wire.i2c import I2CMaster, reading, writing

class NokiaDisplay:
	def __init__(self, i2cSlaveAddr = 0x19, i2cBusNbr = 0):
		self.i2cSlaveAddr = i2cSlaveAddr
		self.i2c = I2CMaster(i2cBusNbr)

	def ClearDisplay(self): # sets all pixels to white
		self.i2c.transaction(writing(self.i2cSlaveAddr, [0xB0]))
		time.sleep(0.02) # give the micro processor some time to swallow the data

	def UpdateDisplay(self): # send buffer to the LCD
		self.i2c.transaction(writing(self.i2cSlaveAddr, [0xB1]))
		time.sleep(0.05) # give the micro processor some time to swallow the data

	def SetContrast(self, val): # adjust the contrast. max is 0x7F
		self.i2c.transaction(writing(self.i2cSlaveAddr, [0xB2, val]))
		time.sleep(0.02) # give the micro processor some time to swallow the data

	def TextOut(self, xpos, ypos, text, big = False): # write text at a given position
		data = [0xB3, xpos, ypos, 1 if big == True else 0, len(text)]
		for i in range(len(text)):
			data.append(ord(text[i]))
		self.i2c.transaction(writing(self.i2cSlaveAddr, data))
		time.sleep(0.05) # give the micro processor some time to swallow the data

	def SetPixel(self, xpos, ypos, val = 1): # set a single pixel : 0:white  1:black  2:xor
		self.i2c.transaction(writing(self.i2cSlaveAddr, [0xB4, xpos, ypos, val]))
		time.sleep(0.02)

	def LineOut(self, x1, y1, x2, y2, val = 1): # draw a line -> val : 0:white  1:black  2:xor
		self.i2c.transaction(writing(self.i2cSlaveAddr, [0xB5, x1, y1, x2, y2, val]))
		time.sleep(0.05) # give the micro processor some time to swallow the data

	def StartScreen(self):                     # show the start screen
		self.i2c.transaction(writing(self.i2cSlaveAddr, [0xB6]))
		time.sleep(0.1) # give the micro processor some time to swallow the data

	def Backlight(self, Enable): # draw a line -> val : 0:white  1:black  2:xor
		if Enable:
			self.i2c.transaction(writing(self.i2cSlaveAddr, [0xC1]))
		else:
			self.i2c.transaction(writing(self.i2cSlaveAddr, [0xC2]))
		time.sleep(0.03)

	def LedRed(self, val): # set the brightness of the red LED -> 0-255
		self.i2c.transaction(writing(self.i2cSlaveAddr, [0xC3, val]))
		time.sleep(0.02)

	def LedGreen(self, val): # set the brightness of the green LED -> 0-255
		self.i2c.transaction(writing(self.i2cSlaveAddr, [0xC4, val]))
		time.sleep(0.02)

	def LedBlue(self, val): # set the brightness of the blue LED -> 0-255
		self.i2c.transaction(writing(self.i2cSlaveAddr, [0xC5, val]))
		time.sleep(0.02)

	def PlayTone(self, frequency, duration): # play a tone on the piezzo buzzer
		self.i2c.transaction(writing(self.i2cSlaveAddr, [0xCA, frequency, duration]))
		time.sleep(0.02)

	def LoadGlyph(self, xpos, ypos, filename): # load a glyph from the local filesystem and show it on the display
		self.GlyphToEeprom(filename, 0) 
		im = Image.open(filename)
		self.LoadGlyphFromEeprom(xpos, ypos, 0, im.size[0], im.size[1])

	def GlyphToEeprom(self, filename, addr):
		# the i2c function can transfer may 32 bytes, so we optimize for that
		im = Image.open(filename)
		bytesPerRow = int(math.ceil(float(im.size[0]) / 8))
		pix = im.load()
		data = [0xD1]
		for j in range(im.size[1]): # for all rows
			curraddr = addr + j * bytesPerRow
			if len(data) == 1:
				data = [0xD1, curraddr >> 8, curraddr & 0xFF, bytesPerRow] # address, num bytes
			else:
				data[3] = data[3] + bytesPerRow

			for i in range(bytesPerRow):
				bb = 0
				for k in range(8): # for every bit in the byte
					xx = i * 8 + k
					if xx < im.size[0]:
						pixel = pix[xx, j]
						if im.mode != 'P':
							pxbri = pixel[0] + pixel[1] + pixel[2]	
							if pxbri < 300:
								bb |= 0x1 << k
						else:
							if pixel != 0:
								bb |= 0x1 << k
				data.append(bb)
			if len(data) + bytesPerRow > 31:
				self.i2c.transaction(writing(self.i2cSlaveAddr, data)) # transfer data to eeprom
				time.sleep(0.18) # give the micro processor some time to swallow the data
				data = [0xD1]
		if len(data) > 0:
			self.i2c.transaction(writing(self.i2cSlaveAddr, data)) # transfer data to eeprom
			time.sleep(0.18) # give the micro processor some time to swallow the data


	def LoadGlyphFromEeprom(self, xpos, ypos, addr, sizeX = 32, sizeY = 32):
		data = [0xD2, xpos, ypos, addr >> 8, addr & 0xFF, sizeX, sizeY]
		self.i2c.transaction(writing(self.i2cSlaveAddr, data))
		time.sleep(0.02) # give the micro processor some time to swallow the data

	def AnimateGlyphsFromEeprom(self, numloop, delay, positions, addrs, sizeX = 32, sizeY = 32):
		if len(positions) != 2 * len(addrs):
			raise RuntimeError('number of positions and addresses dont match')
		numimg = len(addrs)
		data = [0xD3, numimg, numloop, delay, sizeX, sizeY]
		for i in range(2 * numimg):
			data.append(positions[i])
		for i in range(numimg):
			data.append(addrs[i] >> 8)
			data.append(addrs[i] & 0xFF)
		self.i2c.transaction(writing(self.i2cSlaveAddr, data))
		time.sleep(0.02) # give the micro processor some time to swallow the data

	def __repr__(self):
		print("atmega interfacing a nokia display at i2c address %d" % self.i2cSlaveAddr)



# test code
if __name__ == "__main__":
	disp = NokiaDisplay(0x19, 0) # bus is 0 on the alix, and 1 on the raspbe
	disp.Backlight(True)
#	disp.LedBlue(130)
	disp.ClearDisplay()
	disp.UpdateDisplay()
#	time.sleep(0.5)
	disp.LedBlue(0)
#	disp.StartScreen()
	disp.UpdateDisplay()
#	time.sleep(1.0)
	disp.ClearDisplay()
	disp.UpdateDisplay()
	disp.SetContrast(0x40)
	time.sleep(0.1)
	disp.LineOut(5, 5, 40, 20, 1)
	disp.UpdateDisplay()
	time.sleep(0.1)
	disp.TextOut(4, 1, "Hello World")
	disp.UpdateDisplay()
	time.sleep(0.1)
	disp.LoadGlyph(55, 14, 'glyph/beer32.png')
	disp.GlyphToEeprom('glyph/RICHARD.ULRICH.png', 0)
	positions = [20, 14, 24, 14, 28, 14, 32, 14, 36, 14, 40, 14]
	addrs = [0, 0, 0, 0, 0, 0]
	disp.AnimateGlyphsFromEeprom(1, 10, positions, addrs, 23, 32)
	time.sleep(1.0)
	disp.GlyphToEeprom('glyph/ANDREAS.BURCH.png', 128)
	disp.GlyphToEeprom('glyph/GABRIEL.BOCEK.png', 256)
	disp.GlyphToEeprom('glyph/RETO.CONCONI.png', 384)
	positions = [40, 14, 40, 14, 40, 14, 40, 14]
	addrs = [128, 256, 384, 0]
	disp.AnimateGlyphsFromEeprom(1, 50, positions, addrs, 23, 32)
	time.sleep(2.0)
	disp.Backlight(False)	


