#!D:/Python27/python.exe -u
# -*- coding: utf-8 -*-

'''
This little script fetch the textvalues from the following tables:
sbk_bf_pp_projekt_nbr_bostad
sbk_bf_pp_projekt

It uses the relations module to translate id's into text for planskede and 
other info.
sbk_pp_projekt_nbr_bostad data is parsed in objects based on year.
Projekt and bostad data is merged by projekt id and returned 
as a list inside a JSON.
'''

__version__ = '1.0'
__author__ = 'Peter Ahlström'


# import time
import json
import relations
import cgitb
import cx_Oracle
# import datetime
# import sys
import config

# cgitb.enable()	#for debug in browser

# response list structure
rl = {
		'projekt': ['id', 'namn', 'anteckning', 'projekt_skede_id', 'plan_person_id', 'plan_skede_id', 'detaljplan'],
		'bostad': ['projekt_id', 'totalt_start', 'totalt_tilldelat', 'totalt_mkb', 'datum_start', 'datum_tilldelat', 'datum_tilldelat_mkb'],
	}

def main():
	con = cx_Oracle.connect(config.ORACLE_CONNECTION_STRING)
	cur = con.cursor()

	bostad_query = ("SELECT * FROM sbk_bf_pp_projekt_nbr_bostad")
	projekt_query = ("SELECT * FROM sbk_bf_pp_projekt")

	bostad_list = query(cur, bostad_query)
	projekt_list = query(cur, projekt_query)

	cur.close()
	con.close()

	projekt = parse_projekt(projekt_list)
	bostad = parse_bostad(bostad_list)

	output = merge_tables(projekt, bostad)

	print 'Content-Type: application/json\n\n'
	print json.dumps(output)
	# write_file(json.dumps(output)) #DEBUG


#DEBUG
def write_file(output):
	with open('Y:\\bostad\\data\\dump.json', 'w') as f:
		f.write(output)

def merge_tables(projekt, bostad):
	for i in bostad.keys():
		projekt[i].update(bostad[i])

	out = []
	for i in projekt.items():
		out.append(i[1])

	return out

def query(cursor, query):
	cursor.execute(query)
	return cursor.fetchall()

def create_objects_from_db_response(response_list, category):
	output = []

	if category == 'bostad':
		row_list = []
		for row in response_list:

			temp_row = {}	
			for index, col in enumerate(row):
				key = rl[category][index]
				temp_row[key] = col

				if key == 'datum_tilldelat':
					year = temp_row[key].year
					temp_row[str(year) + '_tilldelat'] = temp_row['totalt_tilldelat']
				else:
					temp_row[str(year) + '_tilldelat'] = ' '
				if key == 'datum_start':
					year = temp_row[key].year
					temp_row[str(year) + '_start'] = temp_row['totalt_start']
				else:
					temp_row[str(year) + '_start'] = ' '
				if key == 'datum_tilldelat_mkb':
					year = temp_row[key].year
					temp_row[str(year) + '_tilldelat_mkb'] = temp_row['totalt_mkb']
				else:
					temp_row[str(year) + '_tilldelat_mkb'] = ' '
				print temp_row
				print '\n'
				output.append(temp_row)
	else:
		for row in response_list:
			temp_row = {}	
			for index, col in enumerate(row):
				temp_row[rl[category][index]] = col
			output.append(temp_row)
	return output

def create_lists_from_db_response(response_list, category):
	output = []

	for row in response_list:
		temp_row = {}	
		for index, col in enumerate(row):
			output.append({[rl[category][index]]: col})
	return output

def parse_bostad(resp_list):
	bostad = {}

	for row in resp_list:
	    projekt_id = row[0]
	    year_start = str(row[4].year)
	    year_tilldelat = str(row[5].year)
	    year_mkb = str(row[6].year)

	    if projekt_id not in bostad:
	   		bostad[projekt_id] = {}
	    bostad[projekt_id][year_start + '_start'] = row[1] or ' '
	    bostad[projekt_id][year_tilldelat + '_tilldelat'] = row[2] or ' '
	    bostad[projekt_id][year_mkb + '_mkb'] = row[3] or ' '

	return bostad


def parse_projekt(resp_list):
	rel = relations.Relations()
	resp_rows = create_objects_from_db_response(resp_list, 'projekt')

	for output in resp_rows:
		if output['plan_person_id'] != None:
			#get person name from relations table
			person_dict = json.loads(rel.req_person(output['plan_person_id']))
			output['plan_person_text'] = person_dict['person_text']
		else:
			output['plan_person_text'] = ' '

		if output['plan_skede_id'] != None:
			#get planskede from relations table
			skede_plan = json.loads(rel.req_skede_plan(output['plan_skede_id']))
			output['skede_plan_text'] = skede_plan['skede_plan_text']
		else:
			output['skede_plan_text'] = ' '

		if output['projekt_skede_id'] != None:
			#get projektskede from relations table
			skede_projekt = json.loads(rel.req_skede_projekt(output['projekt_skede_id']))
			output['skede_projekt_text'] = skede_projekt['skede_projekt_text']
		else:
			output['skede_projekt_text'] = ' '

		try:
			detaljplan = json.loads(rel.req_plan(output['id']))
			output['detaljplan'] = detaljplan['detaljplan']
		except Exception, e:
			pass

	op = {}
	for row in resp_rows:
		op[row['id']] = row
	return op

if __name__ == '__main__':
	main()
