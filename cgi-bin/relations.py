#!D:\Python27\python.exe -u
# -*- coding: utf-8 -*-

'''
This little module is used to translate id value to text-values or the 
opposite from the following tables:
sbk_bf_pp_skede_plan			
sbk_bf_pp_skede_projekt			
namn_kort FROM sbk_bf_pp_plan_person			
sbk_bf_pp_projekt_plan		
'''

__version__ = '1.0'
__author__ = 'Peter Ahlström'


import cgi
import cgitb
import sys
import json
import cx_Oracle
import os
import config

# set db charset
os.environ["NLS_LANG"] = ".UTF8"

class Relations:

	db_url = config.ORACLE_CONNECTION_STRING

	def __init__(self):
		self.tables = self.get_tables()
	
	def connect(self):
		self.con = cx_Oracle.connect(self.db_url)
		self.cur = self.con.cursor()
		
	def disconnect(self):
		self.cur.close()
		self.con.close()

	def merge_multiple_rows(self, db_resp):
		temp = []
		output = {}

		for row in db_resp:
			if row[0] in temp:
				output[row[0]].append(row[1])
			else:
				temp.append(row[0])
				output[row[0]] = [row[1]]

		for key, value in output.iteritems():
			if len(value) > 1:
				output[key] = ', '.join(value)
			else:
				output[key] = value[0]

		return output.items()


	def get_table(self, query):
		self.cur.execute(query)
		db_resp = self.cur.fetchall()
		return self.merge_multiple_rows(db_resp)

	def get_tables(self):
		self.connect()
		tables = {
			'skede_plan': "SELECT * FROM sbk_bf_pp_skede_plan",
			'skede_projekt': "SELECT * FROM sbk_bf_pp_skede_projekt",
			'plan_person': "SELECT id, namn_kort FROM sbk_bf_pp_plan_person",
			'detaljplan': "SELECT * FROM sbk_bf_pp_projekt_plan"
		}
		for key, value in tables.iteritems():
			tables[key] = dict(self.get_table(value))
		self.disconnect()

		tables = self.invert_tables(tables)
		return tables

	def invert_tables(self, tables):
		temp = {}
		for key, value in tables.iteritems():
			temp[key + '_inv'] = dict((v, k) for k, v in value.iteritems())

		tables.update(temp)
		return tables


	def req_skede_plan(self, skede_plan_id):
		if skede_plan_id in self.tables['skede_plan']:
			return json.dumps({'skede_plan_text': self.tables['skede_plan'][skede_plan_id]})

	def req_skede_projekt(self, skede_projekt_id):
		if skede_projekt_id in self.tables['skede_projekt']:
			return json.dumps({'skede_projekt_text': self.tables['skede_projekt'][skede_projekt_id]})

	def req_person(self, person_id):
		if person_id in self.tables['plan_person']:
			return json.dumps({'person_text': self.tables['plan_person'][person_id]})

	def req_plan(self, projekt_id):
		if projekt_id in self.tables['detaljplan']:
			return json.dumps({'detaljplan': self.tables['detaljplan'][projekt_id]})

	#INVERTED
	def req_skede_plan_id(self, skede_plan_text):
		if skede_plan_text in self.tables['skede_plan_inv']:
			return self.tables['skede_plan_inv'][skede_plan_text]

	def req_skede_projekt_id(self, skede_projekt_text):
		if skede_projekt_text in self.tables['skede_projekt_inv']:
			return self.tables['skede_projekt_inv'][skede_projekt_text]

	def req_person_id(self, person_text):
		if person_text in self.tables['plan_person_inv']:
			return self.tables['plan_person_inv'][person_text]		

