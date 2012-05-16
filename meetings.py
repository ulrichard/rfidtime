#! /usr/bin/python

import pymssql
import time
from datetime import date
import time


# connect to the database
print "connecting to the database"
conn = pymssql.connect(
	host = '192.168.111.10', 
	user = 'sa', 
	password = 'guesswhat', 
	database = 'Cubx', 
	as_dict = True
)

userid =   6 # UlR
aufid  = 259 # Borm PointLine Allgemein
kstid  =  14 # 500 Besprechnung

def add_meeting(meet_date, meet_start, meet_end):
	print 'adding meeting %s  from %f to %f' % (meet_date, meet_start, meet_end)
	cur = conn.cursor()
	cur.execute('SELECT * FROM DZ_DATEN WHERE MITARBEITER_ID=%d AND DZ_DATUM=%s AND KOSTENSTELLEN_ID=%d AND DZ_BZ > %f AND DZ_EZ < %f', (userid, meet_date, kstid, meet_start - 0.05, meet_end + 0.05))
	row = cur.fetchone()
	if row:
		if aufid == row['AUF_ID']:
			print 'the meeting is already in the db'
		else:
			cur.execute('UPDATE DZ_DATEN SET AUF_ID=%d WHERE DZ_DATEN_ID=%d', (aufid, row['DZ_DATEN_ID']))
			print 'changed AUF_ID of record %d' % row['DZ_DATEN_ID']
#		conn.rollback()  # for testing
		conn.commit()
		return

	cur.execute('SELECT * FROM DZ_DATEN WHERE MITARBEITER_ID=%d AND DZ_DATUM=%s ORDER BY DZ_BZ ASC', (userid, meet_date))
	row = cur.fetchone()
	while row:
		rec_start = row['DZ_BZ']
		rec_end   = row['DZ_EZ']
		rec_id    = row['DZ_DATEN_ID']
		rec_chg   = False

		if rec_start >= meet_start and rec_end <= meet_end:
			cur.execute('UPDATE DZ_DATEN SET KOSTENSTELLEN_ID=%d WHERE DZ_DATEN_ID=%d', (kstid, rec_id))
			print 'changed kst of record %d' % row['DZ_DATEN_ID']
			return
		if rec_start > meet_end or rec_end < meet_start:
			row = cur.fetchone()
			continue

		if rec_start >= meet_start:
			meet_start = rec_start
		else:
			cur.execute('UPDATE DZ_DATEN SET DZ_EZ=%f, DZ_IST=%f WHERE DZ_DATEN_ID=%d', (meet_start, meet_start - rec_start, rec_id))
			print 'adjusted end time of record %d' % row['DZ_DATEN_ID']
			rec_chg = True
		if rec_end <= meet_end:
			meet_end = rec_end
		elif not rec_chg:
			cur.execute('UPDATE DZ_DATEN SET DZ_BZ=%f, DZ_IST=%f WHERE DZ_DATEN_ID=%d', (meet_end, rec_end - meet_end, rec_id))
			print 'adjusted start time of record %d' % row['DZ_DATEN_ID']
			rec_chg = True
		else:
			cur.execute('INSERT INTO DZ_DATEN '
			'(MITARBEITER_ID, AUF_ID, KOSTENSTELLEN_ID, DZ_TAET_ID, DZ_DATUM, ZM_ID, DZ_BZ, DZ_EZ, DZ_IST, EROEFFNUNGSDATUM, OPEN_USER, AENDERUNGSDATUM, CURRENTUSER) VALUES '
			'(%d, %d, %d, %d, %s, %d, %f, %f, %f, GETDATE(), %s, GETDATE(), %s)', 
			(row['MITARBEITER_ID'], row['AUF_ID'], row['KOSTENSTELLEN_ID'], row['DZ_TAET_ID'], row['DZ_DATUM'], row['ZM_ID'], meet_end, rec_end, rec_end - meet_end, row['OPEN_USER'], row['CURRENTUSER']))
			print 'inserted a new record for the second part of regular work'

		cur.execute('INSERT INTO DZ_DATEN '
			'(MITARBEITER_ID, AUF_ID, KOSTENSTELLEN_ID, DZ_TAET_ID, DZ_DATUM, ZM_ID, DZ_BZ, DZ_EZ, DZ_IST, EROEFFNUNGSDATUM, OPEN_USER, AENDERUNGSDATUM, CURRENTUSER) VALUES '
			'(%d, %d, %d, %d, %s, %d, %f, %f, %f, GETDATE(), %s, GETDATE(), %s)', 
			(row['MITARBEITER_ID'], row['AUF_ID'], kstid, row['DZ_TAET_ID'], row['DZ_DATUM'], row['ZM_ID'], meet_start, meet_end, meet_end - meet_start, row['OPEN_USER'], row['CURRENTUSER']))
		print "added a new record for the meeting"

#		conn.rollback()  # for testing
		conn.commit()
		return
			
	print "no matching record"


# add the meeting times here
add_meeting('2012-04-13', 16.00, 17.25)
add_meeting('2012-04-27', 16.00, 17.00)
add_meeting('2012-04-02', 10.50, 12.63)
add_meeting('2012-04-10', 11.00, 11.30)
add_meeting('2012-04-16', 14.35, 14.80)
add_meeting('2012-04-23', 14.00, 14.50)
add_meeting('2012-04-30', 10.37, 10.85)
add_meeting('2012-05-07', 11.05, 11.30)
add_meeting('2012-05-11', 14.80, 16.75)
add_meeting('2012-05-15', 11.20, 11.45)

conn.close()




