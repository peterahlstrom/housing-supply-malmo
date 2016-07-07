#!D:\Python27\python.exe -u
# -*- coding: utf-8 -*-

'''
This little script takes a POST-request with a table row as JSON and insert into table sbk_bf_pp_plan_person.
Indata example:
{
	"id": 'kfjhkf34i6856,
	"namn": "PETAHL"
}
It returns a JSON with status for the operation.
'''

__version__ = '1.0'
__author__ = 'Peter Ahlström'


# import time
import json
import relations
import cgitb
import cx_Oracle
# import datetime
import sys
# import cgi
# import os
import re
import config

cgitb.enable()	#for debug in browser

def main():
	indata = json.load(sys.stdin)
	insert_status = insert_row(indata)

	print 'Content-Type: application/json\n\n'
	print json.dumps(insert_status)

def insert_row(indata):
	try:
		namn = indata['namn']
		con = cx_Oracle.connect(config.ORACLE_CONNECTION_STRING)
		cur = con.cursor()
		projekt_statement = 'INSERT INTO sbk_bf_pp_plan_person (namn_kort) VALUES (:namn)'
		cur.execute(projekt_statement, {'namn':namn})
		con.commit()

		cur.close()
		con.close()
		return {'status': 'success'}

	except cx_Oracle.DatabaseError as error:
		(e,) = error.args
		return {'status': 'Oracle error code: %s | Context: %s |  %s' % (e.code, e.context, e.message)}
		cur.close()
		con.close()

if __name__ == '__main__':
	main()
