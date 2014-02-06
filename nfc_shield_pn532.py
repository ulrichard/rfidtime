#! /usr/bin/python2
# script to communicate with the nfc shield
# http://www.elecfreaks.com/store/rfidnfc-breakout-board-p-519.html
# https://www.adafruit.com/products/364
# http://nfc-tools.org/index.php?title=Libnfc#Debian_.2F_Ubuntu
# http://packages.debian.org/source/sid/libnfc
# http://hubcitylabs.org/nfc-on-raspberrypi-with-pn532-py532lib-and-i2c/

import time, math, os, sys

lib_path = os.path.abspath('.')
sys.path.append(lib_path + '/rfid532lib')

from rfid532lib.py532lib.i2c import *
from rfid532lib.py532lib.frame import *
from rfid532lib.py532lib.constants import *


class NfcShield:
	def __init__(self, i2cSlaveAddr = 0x24, i2cBusNbr = 0):
		self.pn532 = Pn532_i2c(i2cSlaveAddr, i2cBusNbr)
		self.pn532.SAMconfigure()

#	def GetFirmwareVersion(self): # Checks the firmware version of the PN5xx chip
#		self.i2c.write_byte(self.i2cSlaveAddr, 0x02) # PN532_COMMAND_GETFIRMWAREVERSION
#		time.sleep(0.002) 
#		data = self.i2c.read_i2c_block_data(self.i2cSlaveAddr, 0x02)
#		return data

	def GetCardData(self, timeout):
		response = self.pn532.read_mifare(timeout)
		if type(str()) == type(response):
			return response
		return response.get_data()

#	def __repr__(self):
		print('This is a library for the Adafruit PN532 NFC shield')


# test code
if __name__ == '__main__':
	nfc = NfcShield(0x24, 1) # bus is 0 on the alix, and 1 on the raspberryPi
#	print nfc.GetFirmwareVersion()

	print(nfc.GetCardData(1))

