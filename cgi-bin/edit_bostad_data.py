#!D:/Python27/python.exe -u
# -*- coding: utf-8 -*-

'''
This little script takes a POST-request with a table row as JSON, 
checkes if row exist in table sbk_bf_pp_projekt_nbr_bostad, then either insert 
or update data.
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

column_names = {
	'category': {
		'start': 'totalt_start',
		'tilldelat': 'totalt_tilldelat',
		'mkb': 'totalt_mkb'
	},
	'date': {
		'start': 'datum_start',
		'tilldelat': 'datum_tilldelat',
		'mkb': 'datum_tilldelat_mkb'
	}
}

statements = {
	'update': {
		'totalt_start': 'UPDATE sbk_bf_pp_projekt_nbr_bostad SET totalt_start = :value WHERE projekt_id = :projekt_id AND EXTRACT(YEAR FROM datum_start) = :year',
		'totalt_tilldelat': 'UPDATE sbk_bf_pp_projekt_nbr_bostad SET totalt_tilldelat = :value WHERE projekt_id = :projekt_id AND EXTRACT(YEAR FROM datum_tilldelat) = :year',
		'totalt_mkb': 'UPDATE sbk_bf_pp_projekt_nbr_bostad SET totalt_mkb = :value WHERE projekt_id = :projekt_id AND EXTRACT(YEAR FROM datum_tilldelat_mkb) = :year'
	},
	'insert': {
		'totalt_start': 'INSERT INTO sbk_bf_pp_projekt_nbr_bostad (projekt_id, totalt_start, datum_start, datum_tilldelat, datum_tilldelat_mkb) VALUES (:projekt_id, :value, :date_start, :date_tilldelat, :date_mkb)',
		'totalt_tilldelat': 'INSERT INTO sbk_bf_pp_projekt_nbr_bostad (projekt_id, totalt_tilldelat, datum_start, datum_tilldelat, datum_tilldelat_mkb) VALUES (:projekt_id, :value, :date_start, :date_tilldelat, :date_mkb)',
		'totalt_mkb': 'INSERT INTO sbk_bf_pp_projekt_nbr_bostad (projekt_id, totalt_mkb, datum_start, datum_tilldelat, datum_tilldelat_mkb) VALUES (:projekt_id, :value, :date_start, :date_tilldelat, :date_mkb)'
	}
}

def main():
	indata = json.load(sys.stdin)
	data = parse_data(indata)

	#global vars so you do not have to pass these around to the functions later
	global con
	global cur

	try:
		con = cx_Oracle.connect(config.ORACLE_CONNECTION_STRING)
		cur = con.cursor()

		if check_if_exist_in_db(data) == True:
			status = update_row(data['update_values'])

		else:
			status = insert_row(data['insert_values'])

		cur.close()
		con.close()


	except cx_Oracle.DatabaseError as error:
		(e,) = error.args
		status = {'status': 'Oracle error code: %s | Context: %s |  %s' % (e.code, e.context, e.message)}
		cur.close()
		con.close()

	print 'Content-Type: application/json\n\n'
	print json.dumps(status)

def check_if_exist_in_db(data):
	try:
		query = "select * from sbk_bf_pp_projekt_nbr_bostad where projekt_id = :id and EXTRACT(YEAR FROM datum_start) = :year"
		cur.execute(query, {'id': data['projekt_id'], 'year': data['year']})
		reply = cur.fetchall()
		if len(reply) > 0:
			return True
		else:
			return False

	except cx_Oracle.DatabaseError as error:
		(e,) = error.args
		return {'status': 'Oracle error code INSERT: %s | Context: %s |  %s' % (e.code, e.context, e.message)}

	return False

def insert_row(values):
	print values['values']
	try:
		statement = statements['insert'][values['category']]
		cur.execute(statement, values['values'])
		con.commit()
		return {'status': 'success'}

	except cx_Oracle.DatabaseError as error:
		(e,) = error.args
		return {'status': 'Oracle error code INSERT: %s | Context: %s |  %s' % (e.code, e.context, e.message)}

def update_row(values):
	try:
		statement = statements['update'][values['category']]
		cur.execute(statement, values['values'])
		con.commit()
		return {'status': 'success'}

	except cx_Oracle.DatabaseError as error:
		(e,) = error.args
		return {'status': 'Oracle error code UPDATE: %s | Context: %s |  %s' % (e.code, e.context, e.message)}

def parse_data(indata):

	data = {}

	projekt_id = indata['id']
	column = indata['column'].split('_')
	year = int(column[0])
	value = indata['value']
	category = column_names['category'][column[1]]
	date = datetime.datetime(year, 4, 1)	#default date is always April 1.

	data['projekt_id'] = projekt_id
	data['category'] = category
	data['year'] = year

	data['update_values'] = {
		'values': {
			'value': value,
			'projekt_id': projekt_id,
			'year': year,
			},
		'category': category
			
		}

	data['insert_values'] = {
		'values': {
			'projekt_id': projekt_id,
			'value': value,
			'date_start': date,
			'date_tilldelat': date,
			'date_mkb': date,
			},
		'category': category
		}

	return data

if __name__ == '__main__':
	main()