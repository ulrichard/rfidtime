#! /usr/bin/python
#for reference see http://code.google.com/p/pymssql/wiki/PymssqlExamples

import pymssql
import time
import serial
import daemon
import configglue
import optparse
from datetime import date
import time
from configobj import ConfigObj
import os
import smbus
from nokia_display import NokiaDisplay
from bamboo import BambooState

#with daemon.DaemonContext():
#    do_main_program()

glyphAddr = {}

def main(config, opts):
	configval = config.values('__main__')

	# stop the annoying default program of the blinkM
	if configval.get('useBlinkM'):
		i2c = smbus.SMBus(0)
		i2c.write_byte(0x09, 0x6f) # 'o' -> stop script
		#dark
		i2c.write_byte(0x09, 0x6e)
		i2c.write_byte(0x09, 0x00)
		i2c.write_byte(0x09, 0x00)
		i2c.write_byte(0x09, 0x00)

	if configval.get('useNokiaDisplay'):
		disp = NokiaDisplay(0x19, configval.get('NokiaDisplayBus'))
		disp.Backlight(True)
		disp.StartScreen()
		time.sleep(0.5)
		disp.Backlight(False)
		disp.LedRed(0)
		disp.LedGreen(0)
		disp.LedBlue(0)
		disp.GlyphToEeprom('glyph/factory32.png', 384)
		disp.GlyphToEeprom('glyph/beer32.png', 512)
		glyphAddr['glyph/factory32.png'] = 384
		glyphAddr['glyph/beer32.png'] = 512

	# connect to the database
	print "connecting to the database"
	conn = pymssql.connect(
		host = configval.get('host'), 
		user = configval.get('user'), 
		password = configval.get('password'), 
		database = configval.get('database'), 
		as_dict = True
	)

	# if a userid was provided at the commandline, handle it and exit
	if configval.get('userid'):
		open_or_close_time_record(conn, int(configval.get('userid')), configval)
		conn.close()
		exit()

	# open the serial connection to the rfid reader
	print "open the serial port"
	ser = serial.Serial(
		port = configval.get('serialport'),
		baudrate = 9600
	)
	ser.open()
	ser.isOpen()
	print ser.portstr

	userconfig = ConfigObj(configval.get('userconfig'))['users'].dict()

	print "listening for rfid tags"
	while 1:
		rfidtag = ''
		timestr = ''
		bambooCountdown = 1
		while len(rfidtag) < 10:
			if ser.inWaiting() == 0:
				time.sleep(0.05)
				tmptimestr = time.strftime('%x %X')[0:14]
				# update the time string once a second
				if timestr != tmptimestr:
					timestr = tmptimestr
					disp.TextOut(1, 6, timestr)
					disp.UpdateDisplay()

					# check the buld status on bamboo once a minute
					bambooCountdown = bambooCountdown - 1
					if bambooCountdown <= 0:
						check_bamboo_state(configval)
						bambooCountdown = 60
				continue
			serin = ser.read(1)
			rfidtag += "%02X" % ord(serin)
		rfidtag = rfidtag[:10]
		print "************************************************"
		print time.strftime('%x %X')
		print "we have an rfid tag: " + rfidtag

		# the mapping from rfid tag to userid would better be done in the database, but for now, the cfg file is ok
		if not rfidtag in userconfig:
			print "Unknown rfid tag : " + rfidtag
			notification(rfidtag, 'Unknown tag', 'red', configval)
			ser.flushInput()
			continue

		userid = int(userconfig[rfidtag])
		if userid:
			open_or_close_time_record(conn, userid, configval)
		time.sleep(2.0)
		ser.flushInput()

	conn.close()

	ser.close()
	exit()


def open_or_close_time_record(dbconn, userid, configval):
	cur = dbconn.cursor()
	cur.execute('SELECT TOP 1 * FROM DZ_DATEN WHERE MITARBEITER_ID=%d ORDER BY DZ_DATUM DESC, DZ_BZ DESC', userid)
	row = cur.fetchone()
	if not row:
		print "no records for this user. Please start tracking time with the desktop application!"

		notification(userid, 'no records for this user', 'red', configval)

	else:
		print "last record : %d, %d, %s, %s, %s, %s" % (row['DZ_DATEN_ID'], row[1], row['CURRENTUSER'], row['DZ_DATUM'], row['DZ_BZ'], row['DZ_EZ'])
	  
		now = time.localtime()
		industrynow = now.tm_hour + (now.tm_min + (now.tm_sec / 60.0)) / 60.0
		if (row['DZ_EZ'] is None or row['DZ_EZ'] == 0) and date.today() == row['DZ_DATUM'].date():
			# just close the current record
			print "closing record " + str(row['DZ_DATEN_ID'])
			cur.execute('UPDATE DZ_DATEN SET DZ_EZ=%f, DZ_IST=%f WHERE DZ_DATEN_ID=%d' % (industrynow, industrynow - row['DZ_BZ'], row['DZ_DATEN_ID']))

			notification(row['CURRENTUSER'], 'geht', 'green', configval)

		else:
			if row['AUF_ID'] is None:
				notification('Auftrag is missing', 'in the last record', 'red', configval)

			# create a new record with mostly the same settings as the last one
			print "The last record is closed. Creating a new record."
			cur.execute('INSERT INTO DZ_DATEN '
				'(MITARBEITER_ID, AUF_ID, KOSTENSTELLEN_ID, DZ_DATUM, ZM_ID, DZ_BZ, EROEFFNUNGSDATUM, OPEN_USER, AENDERUNGSDATUM, CURRENTUSER) VALUES '
				'(%d, %d, %d, %s, %d, %f, GETDATE(), %s, GETDATE(), %s)', 
				(row['MITARBEITER_ID'], row['AUF_ID'], row['KOSTENSTELLEN_ID'], date.today().isoformat(), row['ZM_ID'], industrynow, row['OPEN_USER'], row['CURRENTUSER']))
			
			notification(row['CURRENTUSER'], 'kommt', 'blue', configval)			
			
		if configval.get('writetodb'):
			dbconn.commit()
		else:
			dbconn.rollback()

def notification(who, what, color, configval):
	if configval.get('useNokiaDisplay'):
		disp = NokiaDisplay(0x19, configval.get('NokiaDisplayBus'))
		disp.Backlight(True)
		disp.ClearDisplay()
		disp.TextOut(1, 1, who)
		disp.TextOut(1, 2, what)
		disp.TextOut(1, 6, time.strftime('%x %X')[0:14])
		disp.UpdateDisplay()
		if(color == 'blue'):
			disp.LedBlue(130)
		elif(color == 'green'):
			disp.LedGreen(130)
		elif(color == 'red'):
			disp.LedRed(130)
		if(color == 'blue'):
			disp.GlyphToEeprom('glyph/factory32.png', 384)
			disp.LoadGlyphFromEeprom(55, 8, glyphAddr['glyph/factory32.png'], 32, 32)
		elif(color == 'green'):
                	disp.GlyphToEeprom('glyph/beer32.png', 512)
			disp.LoadGlyphFromEeprom(55, 8, glyphAddr['glyph/beer32.png'], 32, 32)
		time.sleep(0.2)
		disp.LedRed(0)
		disp.LedGreen(0)
		disp.LedBlue(0)
		portrait = 'glyph/%s.png' % who
		if os.path.exists(portrait):
			addr = 0
			if portrait in glyphAddr:
				addr = glyphAddr[portrait]
			else:
				addr = 256
				for k, v in glyphAddr.iteritems():
					if v >= addr:
						addr = v + 128
				glyphAddr[portrait] = addr
			disp.GlyphToEeprom(portrait, addr)
			positions = [20, 8, 24, 8, 28, 8, 32, 8, 36, 8, 40, 8]
			addrs = [addr, addr, addr, addr, addr, addr]
			disp.AnimateGlyphsFromEeprom(1, 10, positions, addrs, 23, 32)
			disp.TextOut(1, 1, who)
			disp.TextOut(1, 2, what)
			disp.TextOut(1, 6, time.strftime('%x %X')[0:14])
		else:
			print 'file not found : ', portrait
		time.sleep(3.0)
		disp.Backlight(False)
		disp.StartScreen()

	if configval.get('useBeep'):
		if(color == 'blue'):
			os.system('beep -f 2000 -l 10 -n -f 1000 -l 10')
		elif(color == 'green'):
			os.system('beep -f 1000 -l 10 -n -f 2000 -l 10')
		elif(color == 'red'):
			os.system('beep -f 1000 -l 100');

	if configval.get('useSpeech'):
		os.system('echo "%s %s" | festival --pipe --tts' % (who, what))

	if configval.get('useBlinkM'): 
		i2c = smbus.SMBus(0)
		if(color == 'blue'):
			i2c.write_byte(0x09, 0x6e)
			i2c.write_byte(0x09, 0x00)
			i2c.write_byte(0x09, 0x00)
			i2c.write_byte(0x09, 0xff)
		elif(color == 'green'):
			i2c.write_byte(0x09, 0x6e)
			i2c.write_byte(0x09, 0x00)
			i2c.write_byte(0x09, 0xff)
			i2c.write_byte(0x09, 0x00)
		elif(color == 'red'):
			i2c.write_byte(0x09, 0x6e)
			i2c.write_byte(0x09, 0xff)
			i2c.write_byte(0x09, 0x00)
			i2c.write_byte(0x09, 0x00)
		time.sleep(2.0);
		i2c.write_byte(0x09, 0x6e)
		i2c.write_byte(0x09, 0x00)
		i2c.write_byte(0x09, 0x00)
		i2c.write_byte(0x09, 0x00)

def check_bamboo_state(configval):
#	print 'checking the bamboo build status on ', configval.get('BambooURL'), '  as  ', configval.get('BambooUser')
	bamb = BambooState(configval.get('BambooURL'), configval.get('BambooUser'), configval.get('BambooPassword'))
	disp = NokiaDisplay(0x19, configval.get('NokiaDisplayBus'))
	disp.LedRed(0)
	disp.LedGreen(0)
	disp.LedBlue(0)
	if not bamb.latestBuildSuccessful('PLB-CIMAINDEV'):
		disp.LedRed(120)
		disp.Backlight(True)
		disp.TextOut(1, 5, 'PLB-CIMAINDEV error')
		disp.UpdateDisplay()
		print ' bamboo PLB-CIMAINDEV error'


if __name__ == '__main__':
    from configglue import schema
    from configglue.glue import configglue

    # create the schema
    class MySchema(schema.Schema):
		host = schema.StringOption(
		    default='192.168.110.31',
		    help='Host where the database engine is listening on')
		database = schema.StringOption(
		    default='Cubx',
		    help='The name of the Database')
		user = schema.StringOption(
		    default='BormUser',
		    help='User name to connect to the database')
		password = schema.StringOption(
		    default='mydirtylittlesecret',
		    help='Password to connecto to the database')
		serialport = schema.StringOption(
		    default='/dev/ttyS0',
		    help='The serial port where the RFID reader is connected')
		userid = schema.StringOption(
		    help='If you pass a userid, the script handles it and exits. Otherwise it listens for RFID tags.')
		userconfig = schema.StringOption(
		    default='/etc/rfidtime.cfg',
		    help='The configuration file where the mapping from rfid tags to user id resides.')
		writetodb = schema.BoolOption(
		    default=False,
		    help='Activate only after the script was approved by Mr. Schwindl.')
		useBlinkM = schema.BoolOption(
			default=False,
			help='Activate visual feedback with a BlinkM connected to I2C bus 0.')
		useBeep = schema.BoolOption(
			default=False,
			help='Activate audio feedback from the beeper.')
		useSpeech = schema.BoolOption(
			default=False,
			help='Activate spoken feedback with the festival text to speech engine.')
		useNokiaDisplay = schema.BoolOption(
			default=False,
			help='Display text on a nokia display connected to an AtMega8 over i2c.')
		NokiaDisplayBus = schema.IntOption(
			default=0,
			help='The i2c bus that the nokia display is connected. 0 on the alix or 1 on the raspberry pi.')
		BambooURL = schema.StringOption(
			default='dev.cubx-software.com:8446',
			help='The URL where bamboo can be reached')
		BambooUser = schema.StringOption(
			default='ulr',
			help='The bamboo or jira user name')
		BambooPassword = schema.StringOption(
			default='mydirtylittlesecret',
			help='The password for the bamboo or jira login')


    # glue everything together
    glue = configglue(MySchema, ['/etc/rfidtime.cfg'])

    # run
    main(glue.schema_parser, glue.options)


