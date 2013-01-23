#! /usr/bin/python

import pymssql
import time
from datetime import date
import time
import configglue
from configobj import ConfigObj


userid =   6 # UlR
aufid  = 259 # Borm PointLine Allgemein
kstid  =  14 # 500 Besprechnung

def main(config, opts):
        configval = config.values('__main__')

        print "connecting to the database"
        conn = pymssql.connect(
                host = configval.get('host'),
                user = configval.get('user'),
                password = configval.get('password'),
                database = configval.get('database'),
                as_dict = True
        )

        userconfig = ConfigObj(configval.get('userconfig'))['meetings'].dict()
	if 'user' in userconfig:
        	userid = userconfig['user']

        # add the meeting times here
#        add_meeting(conn, '2012-12-11', 10.00, 11.50)
#        add_meeting(conn, '2012-12-13', 09.00, 09.50)
        add_meeting(conn, '2013-01-23', 10.20, 12.25) # scrum 
        add_meeting(conn, '2013-01-23', 12.75, 14.00) # scrum 

	conn.close()



def add_meeting(conn, meet_date, meet_start, meet_end):
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
                userconfig = schema.StringOption(
                    default='/etc/rfidtime.cfg',
                    help='The configuration file where the mapping from rfid tags to user id resides.')

    # glue everything together
    glue = configglue(MySchema, ['/etc/rfidtime.cfg'])

    # run
    main(glue.schema_parser, glue.options)


