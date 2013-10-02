#! /usr/bin/python
# script to communicate with the nfc shie 
# http://www.elecfreaks.com/store/rfidnfc-breakout-board-p-519.html
# https://www.adafruit.com/products/364
# http://nfc-tools.org/index.php?title=Libnfc#Debian_.2F_Ubuntu
# http://packages.debian.org/source/sid/libnfc


import smbus, time, math

class NfcShield:
	def __init__(self, i2cSlaveAddr = 0x24, i2cBusNbr = 0):
		self.i2cSlaveAddr = i2cSlaveAddr
		self.i2c = smbus.SMBus(i2cBusNbr)

	def GetFirmwareVersion(self): # Checks the firmware version of the PN5xx chip
#		self.i2c.write_byte(self.i2cSlaveAddr, 0x02) # PN532_COMMAND_GETFIRMWAREVERSION
#		time.sleep(0.002) 
		data = self.i2c.read_i2c_block_data(self.i2cSlaveAddr, 0x02)
		return data

	def __repr__(self):
		print "This is a library for the Adafruit PN532 NFC/RFID shield"



# test code
if __name__ == "__main__":
	nfc = NfcShield(0x24, 1) # bus is 0 on the alix, and 1 on the raspberryPi
	vers = nfc.GetFirmwareVersion()
	print vers

