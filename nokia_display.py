#! /usr/bin/python
# script to send commands to the nokia display over i2c

import smbus, time, math
from PIL import Image

class NokiaDisplay:
	def __init__(self, i2cSlaveAddr = 0x19, i2cBusNbr = 0):
		self.i2cSlaveAddr = i2cSlaveAddr
		self.i2c = smbus.SMBus(i2cBusNbr)

#	def changeSlaveAddress(self, newAddr):
#		self.i2c.write_byte(self.i2cSlaveAddr, 0xA1)
#		self.i2c.write_byte(self.i2cSlaveAddr, newAddr)

	def ClearDisplay(self): # sets all pixels to white
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB0)
		time.sleep(0.02) # give the micro processor some time to swallow the data

	def UpdateDisplay(self): # send buffer to the LCD
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB1)
		time.sleep(0.05) # give the micro processor some time to swallow the data

	def SetContrast(self, val): # adjust the contrast. max is 0x7F
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB2)
		self.i2c.write_byte(self.i2cSlaveAddr, val)
		time.sleep(0.02) # give the micro processor some time to swallow the data

	def TextOut(self, xpos, ypos, text, big = False): # write text at a given position
		data = [xpos, ypos, 1 if big == True else 0, len(text)]
		for i in range(len(text)):
			data.append(ord(text[i]))
		self.i2c.write_i2c_block_data(self.i2cSlaveAddr, 0xB3, data)
		time.sleep(0.05) # give the micro processor some time to swallow the data

	def SetPixel(self, xpos, ypos, val = 1): # set a single pixel : 0:white  1:black  2:xor
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB4)
		self.i2c.write_byte(self.i2cSlaveAddr, xpos)
		self.i2c.write_byte(self.i2cSlaveAddr, ypos)
		self.i2c.write_byte(self.i2cSlaveAddr, val)
		time.sleep(0.02)

	def LineOut(self, x1, y1, x2, y2, val = 1): # draw a line -> val : 0:white  1:black  2:xor
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB5)
		self.i2c.write_byte(self.i2cSlaveAddr, x1)
		self.i2c.write_byte(self.i2cSlaveAddr, y1)
		self.i2c.write_byte(self.i2cSlaveAddr, x2)
		self.i2c.write_byte(self.i2cSlaveAddr, y2)
		self.i2c.write_byte(self.i2cSlaveAddr, val)
		time.sleep(0.05) # give the micro processor some time to swallow the data

	def StartScreen(self):                     # show the start screen
		self.i2c.write_byte(self.i2cSlaveAddr, 0xB6)
		time.sleep(0.1) # give the micro processor some time to swallow the data

	def Backlight(self, Enable): # draw a line -> val : 0:white  1:black  2:xor
		if Enable:
			self.i2c.write_byte(self.i2cSlaveAddr, 0xC1)
		else:
			self.i2c.write_byte(self.i2cSlaveAddr, 0xC2)
		time.sleep(0.02)

	def LedRed(self, val): # set the brightness of the red LED -> 0-255
		self.i2c.write_byte(self.i2cSlaveAddr, 0xC3)
		self.i2c.write_byte(self.i2cSlaveAddr, val)
		time.sleep(0.02)

	def LedGreen(self, val): # set the brightness of the green LED -> 0-255
		self.i2c.write_byte(self.i2cSlaveAddr, 0xC4)
		self.i2c.write_byte(self.i2cSlaveAddr, val)
		time.sleep(0.02)

	def LedBlue(self, val): # set the brightness of the blue LED -> 0-255
		self.i2c.write_byte(self.i2cSlaveAddr, 0xC5)
		self.i2c.write_byte(self.i2cSlaveAddr, val)
		time.sleep(0.02)

	def PlayTone(self, frequency, duration): # play a tone on the piezzo buzzer
		data = [frequency, duration]
		self.i2c.write_i2c_block_data(self.i2cSlaveAddr, 0xCA, data)
		time.sleep(0.02)

	def LoadGlyphOld(self, xpos, ypos, filename, updatePerLine = False): # load a glyph from the local filesystem and show it on the display
		im = Image.open(filename)
		pix = im.load()
		for j in range(im.size[1]):
			for i in range(im.size[0]):
				pixel = pix[i, j]
				pxbri = pixel[0] + pixel[1] + pixel[2]	
				if pxbri < 300:
					self.SetPixel(xpos + i, ypos + j, 1)	
#				else:
#					self.SetPixel(xpos + i, ypos + j, 0)	
			if updatePerLine:
				if j % 4 == 0:
					self.UpdateDisplay()
					time.sleep(0.05)

	def LoadGlyph(self, xpos, ypos, filename): # load a glyph from the local filesystem and show it on the display
		self.GlyphToEeprom(filename, 0) 
		im = Image.open(filename)
		self.LoadGlyphFromEeprom(xpos, ypos, 0, im.size[0], im.size[1])

	def GlyphToEeprom(self, filename, addr):
		im = Image.open(filename)
		pix = im.load()
		for j in range(im.size[1]): # for all rows
			bytesPerRow = int(math.ceil(float(im.size[0]) / 8))
			curraddr = addr + j * bytesPerRow
			data = [curraddr >> 8, curraddr & 0xFF, bytesPerRow] # address, num bytes
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
		#	print data
			self.i2c.write_i2c_block_data(self.i2cSlaveAddr, 0xD1, data) # transfer data to eeprom
			time.sleep(0.028) # give the micro processor some time to swallow the data


	def LoadGlyphFromEeprom(self, xpos, ypos, addr, sizeX = 32, sizeY = 32):
		data = [xpos, ypos, addr >> 8, addr & 0xFF, sizeX, sizeY]
		self.i2c.write_i2c_block_data(self.i2cSlaveAddr, 0xD2, data)
		print data
		time.sleep(0.02) # give the micro processor some time to swallow the data

#	def AnimateGlyphsFromEeprom(self, xpos, ypos, addrs, delay, numloops, sizeX = 32, sizeY = 32):
#		data = [xpos, ypos, delay, numloops, sizeX, sizeY, len(addrs)]
#		for i in range(len(addrs)):
#			data.append(addrs[i] >> 8)
#			data.append(addrs[i] & 0xFF)
#		self.i2c.write_i2c_block_data(self.i2cSlaveAddr, 0xD3, data)

	def __repr__(self):
		print "atmega interfacing a nokia display at i2c address %d" % self.i2cSlaveAddr



# test code
if __name__ == "__main__":
	disp = NokiaDisplay(0x19, 0) # bus is 0 on the alix, and 1 on the raspbe
	disp.Backlight(True)
	disp.LedBlue(130)
	disp.ClearDisplay()
	disp.UpdateDisplay()
	time.sleep(0.5)
	disp.LedBlue(0)
	disp.StartScreen()
	disp.UpdateDisplay()
	time.sleep(1.0)
	disp.ClearDisplay()
	disp.UpdateDisplay()
	disp.SetContrast(0x40)
	time.sleep(0.1)
	disp.LineOut(5, 5, 40, 20, 1)
	disp.UpdateDisplay()
	time.sleep(0.3)
	disp.TextOut(4, 1, "Hello World")
	disp.UpdateDisplay()
	time.sleep(0.02)
	filename = 'glyph/beer32.png'
	im = Image.open(filename)
	print filename, "  ",  im.size
	disp.LoadGlyph(50, 14, filename)
	filename = 'glyph/Richard.Ulrich.png'
	im = Image.open(filename)
	print filename, "  ",  im.size
	disp.LoadGlyph(5, 14, filename)
	disp.GlyphToEeprom('glyph/Richard.Ulrich.png', 0)
	disp.GlyphToEeprom('glyph/Andreas.Burch.png', 128)
	disp.GlyphToEeprom('glyph/Gabriel.Bocek.png', 256)
	disp.GlyphToEeprom('glyph/Reto.Conconi.png', 384)
	addrs = [0, 128]
#	disp.AnimateGlyphsFromEeprom(5, 14, addrs, 20, 3, 23, 32)
	disp.Backlight(False)	


