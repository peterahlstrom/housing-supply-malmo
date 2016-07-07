#!D:\Python27\python.exe -u
# -*- coding: utf-8 -*-

'''
This little script takes a POST-request with a row id as JSON and delete the 
row from table sbk_bf_pp_plan_person
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
import sys
import config


cgitb.enable()	#for debug in browser

def main():
	indata = json.load(sys.stdin)
	insert_status = delete_row(indata)

	print 'Content-Type: application/json\n\n'
	print json.dumps(insert_status)

def delete_row(row_id):
	try:
		con = cx_Oracle.connect(config.ORACLE_CONNECTION_STRING)
		cur = con.cursor()
		statement = 'DELETE FROM sbk_bf_pp_plan_person WHERE id = :id'
		cur.execute(statement, row_id)
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
