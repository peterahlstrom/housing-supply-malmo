#!D:\Python27\python.exe -u
# -*- coding: utf-8 -*-

'''
This little script takes a POST-request with a table row as JSON and updates 
table sbk_bf_pp_projekt.
Indata example:
{
	"id": 72,
	"namn": "Ellstorp",
	"anteckning": "Bygg om!",
	"skede_projekt_text": "Etapp 2 - Utbyggnadsstrategi",
	"plan_person_text": "MAJMOD",
	"skede_plan_text": "Ansökan"
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
import datetime
import sys
import config
# import cgi
# import os

# cgitb.enable()	#for debug in browser

def main():
	indata = json.load(sys.stdin)
	insert_values = parse_data(indata)
	insert_status = insert_row(insert_values)

	print 'Content-Type: application/json\n\n'
	print json.dumps(insert_status)

def insert_row(values):
	d = values

	try:
		con = cx_Oracle.connect(config.ORACLE_CONNECTION_STRING)
		cur = con.cursor()
		statement = 'UPDATE sbk_bf_pp_projekt SET namn = :namn, anteckning = :anteckning, projekt_skede_id = :projekt_skede_id, plan_person_id = :plan_person_id, plan_skede_id = :plan_skede_id WHERE id = :id'
		values = {'id': d['id'], 'namn': d['namn'], 'anteckning': d['anteckning'], 'projekt_skede_id': d['skede_projekt_id'], 'plan_person_id': d['plan_person_id'], 'plan_skede_id': d['skede_plan_id']}
		cur.execute(statement, values)
		con.commit()
		cur.close()
		con.close()
		return {'status': 'success'}

	except cx_Oracle.DatabaseError as error:
		(e,) = error.args
		return {'status': 'Oracle error code: %s | Context: %s |  %s' % (e.code, e.context, e.message)}
		cur.close()
		con.close()

def parse_data(indata):
	rel = relations.Relations()
	d = indata

	#invert relations
	d['plan_person_id'] = rel.req_person_id(d['plan_person_text'].encode('utf-8'))
	d['skede_projekt_id'] = rel.req_skede_projekt_id(d['skede_projekt_text'].encode('utf-8'))
	d['skede_plan_id'] = rel.req_skede_plan_id(d['skede_plan_text'].encode('utf-8'))

	return d

if __name__ == '__main__':
	main()