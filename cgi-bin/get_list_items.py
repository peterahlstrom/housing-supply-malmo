#!D:\Python27\python.exe -u
# -*- coding: utf-8 -*-

'''
This little script fetch the textvalues from the following tables:
sbk_bf_pp_plan_person
sbk_bf_pp_skede_projekt
sbk_bf_pp_skede_plan

Data is returned as lists inside a JSON, one for each table.
'''

__version__ = '1.0'
__author__ = 'Peter Ahlström'


import json
import cgitb
import cx_Oracle
import os
import config

# cgitb.enable()	#for debug in browser

# set Oracle database charset
os.environ["NLS_LANG"] = ".UTF8"

def parse(resp_list):
	#turn list of one element tuples to list of strings
	out = []
	for item in resp_list:
		out.append(item[0])
	return [' '] + out 		# add empty option


def query(cursor, query):
	cursor.execute(query)
	return cursor.fetchall()

def main():
	con = cx_Oracle.connect(config.ORACLE_CONNECTION_STRING)
	cur = con.cursor()

	output = {}
	namn_query = ("SELECT id, namn_kort FROM sbk_bf_pp_plan_person")
	projekt_skede_query = ("SELECT projekt_skede FROM sbk_bf_pp_skede_projekt")
	plan_skede_query = ("SELECT plan_skede FROM sbk_bf_pp_skede_plan")
	

	namn_list = map(lambda namn: {'id':namn[0], 'namn': namn[1]}, query(cur, namn_query))
	projekt_skede_list = parse(query(cur, projekt_skede_query))
	plan_skede_list = parse(query(cur, plan_skede_query))

	output['plan_person_list'] = namn_list
	output['skede_projekt_list'] = projekt_skede_list
	output['skede_plan_list'] = plan_skede_list

	cur.close()
	con.close()

	print 'Content-Type: application/json\n\n'
	print json.dumps(output)
	
if __name__ == '__main__':
	main()
