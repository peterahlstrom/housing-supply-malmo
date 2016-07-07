#!D:\Python27\python.exe -u
# -*- coding: utf-8 -*-

'''
This little script takes a POST-request with a table row as JSON and insert into table sbk_bf_pp_projekt.
Indata example:
{
	"id": 72,
	"namn": "Ellstorp",
	"anteckning": "Bygg om!",
	"skede_projekt_text": "Etapp 2 - Utbyggnadsstrategi",
	"plan_person_text": "MAJMOD",
	"skede_plan_text": "Ansökan",
	"detaljplan": "DP5401, DP5102 DP9865. DP6978,, dp 4587//Dp5874",
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

# cgitb.enable()	#for debug in browser

def main():
	indata = json.load(sys.stdin)
	insert_status = insert_row(indata)

	print 'Content-Type: application/json\n\n'
	print json.dumps(insert_status)

def insert_row(indata):
	try:
		projekt_values = parse_data(indata)
		con = cx_Oracle.connect(config.ORACLE_CONNECTION_STRING)
		cur = con.cursor()
		projekt_statement = 'INSERT INTO sbk_bf_pp_projekt VALUES (:2, :3, :4, :5, :6, :7)'
		cur.execute(projekt_statement, projekt_values)
		con.commit()

		cur.execute('SELECT id from sbk_bf_pp_projekt WHERE namn = :namn', {'namn': projekt_values[1]})
		new_id = cur.fetchone()[0]

		plan_values = parse_detaljplan(indata, new_id)
		cur.bindarraysize = len(plan_values)
		cur.setinputsizes(int, 6)
		plan_statement = 'INSERT INTO sbk_bf_pp_projekt_plan VALUES (:1, :2)'
		cur.executemany(plan_statement, plan_values)

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

	return (None, d['namn'], d['anteckning'], d['skede_projekt_id'], d['plan_person_id'], d['skede_plan_id'])

def parse_detaljplan(indata, new_id):
	projekt_id = new_id
	planer_string = indata['detaljplan'].upper()
	planer = re.findall('DP\s*\d{4}', planer_string)
	planer = map(lambda plan: re.sub('\s+', '', plan), planer)
	values_to_insert = map(lambda plan: (projekt_id, plan), planer)
	return values_to_insert

if __name__ == '__main__':
	main()
