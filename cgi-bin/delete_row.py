#!D:\Python27\python.exe -u
# -*- coding: utf-8 -*-

'''
This little script takes a POST-request with a row id as JSON and delete the 
row from table sbk_bf_pp_projekt
Indata example:
{
	"id": 72,
}
It returns a JSON with status for the operation.
'''

__version__ = '1.0'
__author__ = 'Peter Ahlström'


import time
import json
import relations
import cgitb
import cx_Oracle
# import datetime
import sys
import config
# import cgi
# import os

# cgitb.enable()	#for debug in browser

def main():
	indata = json.load(sys.stdin)
	insert_status = delete_row(indata)

	print 'Content-Type: application/json\n\n'
	print json.dumps(insert_status)

def delete_row(row_id):
	try:
		con = cx_Oracle.connect(config.ORACLE_CONNECTION_STRING)
		cur = con.cursor()
		delete_projekt_statement = 'DELETE FROM sbk_bf_pp_projekt WHERE id = :id'
		cur.execute(delete_projekt_statement, row_id)
		delete_bostad_data_statement = 'DELETE FROM sbk_bf_pp_projekt_nbr_bostad WHERE projekt_id = :id'
		cur.execute(delete_bostad_data_statement, row_id)
		delete_detaljplan_data_statement = 'DELETE FROM sbk_bf_pp_projekt_plan WHERE projekt_id = :id'
		cur.execute(delete_detaljplan_data_statement, row_id)
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
