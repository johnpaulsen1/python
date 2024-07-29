#!/usr/bin/python3
# -*- coding: utf-8 -*-

import psycopg2
import logging
from penguins.son_of import anton

class DBconnect():
	def __init__(self,database,table):
		self.database = database
		self.table = table
		self.user = "postgres"

		try:
			receipe = {
			  "lock_smith": "not happening today",
			  "og_kush_repro": "not happening tomorrow",
			  "bacon": "not happening ever....."
			}
			password = anton.getTheIngredients(receipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the receipe.")
			print("Exception caught: '{}'".format(e))

		self.password = password
		self.host = "x.x.x.x"
		self.port = "5432"


	def testconnect(self):
		try:
			connection = psycopg2.connect(user = self.user,
									  password = self.password,
									  host = self.host,
									  port = self.port,
									  database = self.database)

			cursor = connection.cursor()
			cursor.execute("SELECT version();")
			record = cursor.fetchone()
			#print(record)
			logging.info("DB connection tested OK.")
			return True

		except (Exception, psycopg2.Error) as error :
			logging.error("Error while connecting to PostgreSQL", error)

		finally:
			if(connection):
				cursor.close()
				connection.close()

	def fetchCurrentCMDB(self,table,database,query):
		try:
			connection = psycopg2.connect(user = self.user,
									  password = self.password,
									  host = self.host,
									  port = self.port,
									  database = self.database)

			cursor = connection.cursor()
			# cursor.execute("SELECT * FROM {}".format(table))
			cursor.execute(query)
			record = cursor.fetchall()
			if record != None:
				for r in record:
					return record
			else:
				return False

		except (Exception, psycopg2.Error) as error :
			logging.error("Error while connecting to PostgreSQL", error)

		finally:
			if(connection):
				cursor.close()
				connection.close()
