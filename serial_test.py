#! /usr/bin/python

import serial, time

ser = serial.Serial(
	port = '/dev/ttyS0',
	baudrate = 9600
)

ser.open()
ser.isOpen()

while 1:
	rfidtag = ''
	while len(rfidtag) < 10:
		if ser.inWaiting() == 0:
			time.sleep(0.05)
			continue
		serin = ser.read(1)
		rfidtag += "%02X" % ord(serin)
	rfidtag = rfidtag[:10]
	print "************************************************"
	print time.strftime('%x %X')
	print "we have an rfid tag: " + rfidtag
