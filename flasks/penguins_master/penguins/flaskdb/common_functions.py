#!/usr/bin/python3
import functools
import io
import ast
import os
import sys
import re
import psycopg2
from datetime import datetime
from collections import defaultdict
from flask import session
from werkzeug.exceptions import abort
from penguins.other_utils import general
from penguins.son_of import anton

today = datetime.today().strftime('%Y-%m-%d')
recipe = {
  "lock_smith": "not happening today",
  "og_kush_repro": "not happening tomorrow",
  "bacon": "not happening ever....."
}
domain = "<domain>"

### functions

def testDB_connectivity():
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host = "x.x.x.x",
									port = "5432",
									database = "linux_cmdb")

		cursor = connection.cursor()
		cursor.execute("SELECT version();")
		record = cursor.fetchone()
		if record:
			return True
		else:
			return False

	except (Exception, psycopg2.Error) as error :
		print("Error while connecting to PostgreSQL", error)

	finally:
		#closing database connection.
			if(connection):
				cursor.close()
				connection.close()
				print("PostgreSQL connection is closed")

def getCurrentCMDB():
	server_details = defaultdict(list)

	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database="linux_cmdb")

		cursor = connection.cursor()
		searchQuery = "SELECT * FROM cmdb;"
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		for i in output:
			server_details[i[0]].append(i[1])
			server_details[i[0]].append(i[2])
			server_details[i[0]].append(i[3])
			server_details[i[0]].append(i[4])
			server_details[i[0]].append(i[5])
			server_details[i[0]].append(i[6])
			server_details[i[0]].append(i[7])
			server_details[i[0]].append(i[8])
			server_details[i[0]].append(i[9])
			server_details[i[0]].append(i[10])
		return server_details


	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()


def getSpecficBUsData(dbName, searchQuery):
	server_details = defaultdict(list)

	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database=dbName)

		cursor = connection.cursor()
		cursor.execute(searchQuery)
		output = cursor.fetchall()

		if dbName == 'linux_cmdb':
			for i in output:
				server_details[i[0]].append(i[1])
				server_details[i[0]].append(i[2])
				server_details[i[0]].append(i[3])
				server_details[i[0]].append(i[4])
				server_details[i[0]].append(i[5])
				server_details[i[0]].append(i[6])
				server_details[i[0]].append(i[7])
				server_details[i[0]].append(i[8])
				server_details[i[0]].append(i[9])
				server_details[i[0]].append(i[10])

		if dbName == 'tmc':
			for i in output:
				id = i[0]								# ID
				hostname = i[1]							# hostname
				server_details[hostname].append(i[2])	# Config Manager
				server_details[hostname].append(i[3])	# BU
				server_details[hostname].append(i[4])	# Cost Centre
				server_details[hostname].append(i[5])	# Company Code
				server_details[hostname].append(i[6])	# Server Role
				server_details[hostname].append(i[7])	# Server type
				server_details[hostname].append(i[8])	# Arcitecture
				server_details[hostname].append(i[9])	# OS
				server_details[hostname].append(i[10])	# OS version
				server_details[hostname].append(i[11])	# IP address
				server_details[hostname].append(i[12])	# uptime
				server_details[hostname].append(i[13])	# Last Check in
				server_details[hostname].append(i[14])	# ClamAV
				server_details[hostname].append(i[15])	# ClamDB
				server_details[hostname].append(i[16])	# Clam update
				server_details[hostname].append(i[17])	# Splunk
				server_details[hostname].append(i[18])	# Tetration
				server_details[hostname].append(i[19])	# Flexera
				server_details[hostname].append(i[20])	# Netbackup
				server_details[hostname].append(i[21])	# CheckMK
				server_details[hostname].append(i[22])	# sudo
				server_details[hostname].append(i[23])	# BESAgent
				server_details[hostname].append(i[24])	# ccs
				server_details[hostname].append(i[28])  # tmc
				server_details[hostname].append(i[25])	# greatwall
				server_details[hostname].append(i[26])	# ad_auth
				splunk_id = i[27]						# splunk_id

		return server_details

	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()

### Must fix: this function does the same as getCurrentCMDB just from a different DB with more columns.
### Will need to have the function take input parameters for database and maybe table.

def getCurrentTMC():
	server_details = defaultdict(list)

	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database="tmc")

		cursor = connection.cursor()
		searchQuery = "SELECT * FROM tmc_main;"
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		for i in output:
			id = i[0]								# ID
			hostname = i[1]							# hostname
			server_details[hostname].append(i[2])	# Config Manager
			server_details[hostname].append(i[3])	# BU
			server_details[hostname].append(i[4])	# Cost Centre
			server_details[hostname].append(i[5])	# Company Code
			server_details[hostname].append(i[6])	# Server Role
			server_details[hostname].append(i[7])	# Server type
			server_details[hostname].append(i[8])	# Arcitecture
			server_details[hostname].append(i[9])	# OS
			server_details[hostname].append(i[10])	# OS version
			server_details[hostname].append(i[11])	# IP address
			server_details[hostname].append(i[12])	# uptime
			server_details[hostname].append(i[13])	# Last Check in
			server_details[hostname].append(i[14])	# ClamAV
			server_details[hostname].append(i[15])	# ClamDB
			server_details[hostname].append(i[16])	# Clam update
			server_details[hostname].append(i[17])	# Splunk
			server_details[hostname].append(i[18])	# Tetration
			server_details[hostname].append(i[19])	# Flexera
			server_details[hostname].append(i[20])	# Netbackup
			server_details[hostname].append(i[21])	# CheckMK
			server_details[hostname].append(i[22])	# sudo
			server_details[hostname].append(i[23])	# BESAgent
			server_details[hostname].append(i[24])	# ccs
			server_details[hostname].append(i[28])  # tmc
			server_details[hostname].append(i[25])	# greatwall
			server_details[hostname].append(i[26])	# ad_auth
			splunk_id = i[27]						# splunk_id

		return server_details


	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()


def getHostfromTMC(host):
	server_details = {}
	server_facts = [
			'config_manager',
			'bu',
			'cost_centre',
			'company_code',
			'server_role',
			'server_type',
			'arch',
			'ostype',
			'osversion',
			'ipaddress',
			'uptime',
			'last_checkin',
			'clamav',
			'clamdb',
			'clam_update',
			'splunk',
			'tetration',
			'flexera',
			'netbackup',
			'checkmk',
			'sudo',
			'besagent',
			'ccs',
			'tmc',
			'greatwall',
			'ad_auth'
			]

	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database="tmc")

		cursor = connection.cursor()
		searchQuery = "SELECT * FROM tmc_main where hostname = '{}';".format(host)
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		if len(output) > 0:
			for i in output:
				id = i[0]									# ID
				server_details['hostname'] = i[1]			# Hostname
				server_details['config_manager'] = i[2]		# Config Manager
				server_details['bu'] = i[3]					# BU
				server_details['cost_centre'] = i[4]		# Cost Centre
				server_details['company_code'] = i[5]		# Company Code
				server_details['server_role'] = i[6]		# Server Role
				server_details['server_type'] = i[7]		# Server type
				server_details['arch'] = i[8]				# Arcitecture
				server_details['ostype'] = i[9]				# OS
				server_details['osversion'] = i[10]			# OS version
				server_details['ipaddress'] = i[11]			# IP address
				server_details['uptime'] = i[12]			# uptime
				server_details['last_checkin'] = i[13]		# Last Check in
				server_details['clamav'] = i[14]			# ClamAV
				server_details['clamdb'] = i[15]			# ClamDB
				server_details['clam_update'] = i[16]		# Clam update
				server_details['splunk'] = i[17]			# Splunk
				server_details['tetration'] = i[18]			# Tetration
				server_details['flexera'] = i[19]			# Flexera
				server_details['netbackup'] = i[20]			# Netbackup
				server_details['checkmk'] = i[21]			# CheckMK
				server_details['sudo'] = i[22]				# sudo
				server_details['besagent'] = i[23]			# BESAgent
				server_details['ccs'] = i[24]				# ccs
				server_details['tmc'] = i[28]               # tmc
				server_details['greatwall'] = i[25]			# greatwall
				server_details['ad_auth'] = i[26]			# ad_auth
				splunk_id = i[27]            				# splunk_id

			return server_details
		else:
			server_details['hostname'] = host
			for i in server_facts:
				server_details[i] = "None"
			return server_details

	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()

def getByFactFromTMC(fact,fact_detail):
	server_details = {}
	table="tmc_main"
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database="tmc")

		cursor = connection.cursor()
		searchQuery = "SELECT * FROM {} where {} = '{}';".format(table, fact, fact_detail)
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		if len(output) > 0:
			for i in output:
				id = i[0]									# ID
				server_details['hostname'] = i[1]			# Hostname
				server_details['config_manager'] = i[2]		# Config Manager
				server_details['bu'] = i[3]					# BU
				server_details['cost_centre'] = i[4]		# Cost Centre
				server_details['company_code'] = i[5]		# Company Code
				server_details['server_role'] = i[6]		# Server Role
				server_details['server_type'] = i[7]		# Server type
				server_details['arch'] = i[8]				# Arcitecture
				server_details['ostype'] = i[9]				# OS
				server_details['osversion'] = i[10]			# OS version
				server_details['ipaddress'] = i[11]			# IP address
				server_details['uptime'] = i[12]			# uptime
				server_details['last_checkin'] = i[13]		# Last Check in
				server_details['clamav'] = i[14]			# ClamAV
				server_details['clamdb'] = i[15]			# ClamDB
				server_details['clam_update'] = i[16]		# Clam update
				server_details['splunk'] = i[17]			# Splunk
				server_details['tetration'] = i[18]			# Tetration
				server_details['flexera'] = i[19]			# Flexera
				server_details['netbackup'] = i[20]			# Netbackup
				server_details['checkmk'] = i[21]			# CheckMK
				server_details['sudo'] = i[22]				# sudo
				server_details['besagent'] = i[23]			# BESAgent
				server_details['ccs'] = i[24]				# ccs
				server_details['tmc'] = i[28]               # tmc
				server_details['greatwall'] = i[25]			# greatwall
				server_details['ad_auth'] = str(i[26])		# ad_auth
				splunk_id = i[27]            				# splunk_id

			return server_details
		else:
			server_details['hostname'] = None
			for i in 'BU','Cost_Centre','Company_Code','role','host_type','architecture','osfamily','osversion','ipaddress':
				server_details[i] = "None"
			return server_details


	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()

def searchByFactTMC(fact,fact_detail):
	server_details = {}
	server_list = []
	table="tmc_main"
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database="tmc")

		cursor = connection.cursor()
		searchQuery = "SELECT * FROM {} where {} = '{}';".format(table, fact, fact_detail)
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		# print(output)
		if len(output) > 0:
			for i in output:
				id = i[0]
				server_details['hostname'] = i[1]
				server_list.append(server_details['hostname'])

			return server_list
		else:
			server_details['hostname'] = None
			for i in [	'config_manager', 'BU', 'cost_centre', 'company_code',
						'role', 'host_type', 'architecture', 'osfamily',
						'osversion','ipaddress', 'uptime', 'last_checkin',
						'clamav_version', 'clamdb_version', 'clam_update',
						'splunk', 'tetration', 'flexera', 'netbackup', 'checkmk',
						'sudo', 'besagent', 'ccs', 'tmc', 'greatwall', 'ad_auth']:
				server_details[i] = "None"
			return server_details


	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()

######################################################3

def getHost(host):
	server_details = {}
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database="linux_cmdb")

		cursor = connection.cursor()
		searchQuery = "SELECT * FROM cmdb where host_name = '{}';".format(host)
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		print("TEST")
		if len(output) > 0:
			for i in output:
				server_details['host_name'] = i[0]
				server_details['BU'] = i[1]
				server_details['Cost_Centre'] = i[2]
				server_details['Company_Code'] = i[3]
				server_details['role'] = i[4]
				server_details['host_type'] = i[5]
				server_details['architecture'] = i[6]
				server_details['osfamily'] = i[7]
				server_details['osversion'] = i[8]
				server_details['ipaddress'] = i[9]
				server_details['managed'] = i[10]
			return server_details
		else:
			server_details['host_name'] = host
			for i in 'BU','Cost_Centre','Company_Code','role','host_type','architecture','osfamily','osversion','ipaddress','managed':
				server_details[i] = "None"

			return server_details

	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()

def getHostByFact(search_item,database,table,fact):
	server_details = {}
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database=database)
								   #database="linux_cmdb")

		cursor = connection.cursor()
		searchQuery = "SELECT * FROM {} where {} = '{}';".format(table,fact,search_item)
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		# print(output)
		if len(output) > 0:
			for i in output:
				server_details['host_name'] = i[0]
				server_details['BU'] = i[1]
				server_details['Cost_Centre'] = i[2]
				server_details['Company_Code'] = i[3]
				server_details['role'] = i[4]
				server_details['host_type'] = i[5]
				server_details['architecture'] = i[6]
				server_details['osfamily'] = i[7]
				server_details['osversion'] = i[8]
				server_details['ipaddress'] = i[9]
				server_details['managed'] = i[10]
			return server_details
		else:
			server_details['host_name'] = "None"
			for i in 'BU','Cost_Centre','Company_Code','role','host_type','architecture','osfamily','osversion','ipaddress','managed':
				server_details[i] = "None"
			return server_details

	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()

# old way of doing it - can only query one DB statically
def getFactfromDB(database,table,fact):
	item_list = ['select']
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database=database)

		cursor = connection.cursor()
		searchQuery = "SELECT {} FROM {}".format(fact,table)
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		for i in output:
			h = i[0].strip()
			if h not in item_list:
				item_list.append(h)
		return item_list


	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()

def getItemfromDB(column,item):
	server_details = defaultdict(list)
	path = os.getcwd() + '/penguins/static/result_export_' + today + '.csv'
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database="linux_cmdb")


		cursor = connection.cursor()
		searchQuery = "SELECT * FROM cmdb WHERE " + column + " = '{}';".format(item)
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		for i in output:
			server_details[i[0]].append(i[1])
			server_details[i[0]].append(i[2])
			server_details[i[0]].append(i[3])
			server_details[i[0]].append(i[4])
			server_details[i[0]].append(i[5])
			server_details[i[0]].append(i[6])
			server_details[i[0]].append(i[7])
			server_details[i[0]].append(i[8])
			server_details[i[0]].append(i[9])
			server_details[i[0]].append(i[10])

		return server_details


	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()

def searchDB(item):
	server_details = defaultdict(list)
	path = os.getcwd() + '/penguins/static/result_export_' + today + '.csv'
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database="linux_cmdb")


		cursor = connection.cursor()
		searchQuery = "SELECT * FROM cmdb WHERE ipaddress = " + "'{}';".format(item)
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		for i in output:
			server_details['host_name'] = i[0]
			server_details['BU'] = i[1]
			server_details['Cost_Centre'] = i[2]
			server_details['Company_Code'] = i[3]
			server_details['role'] = i[4]
			server_details['host_type'] = i[5]
			server_details['architecture'] = i[6]
			server_details['osfamily'] = i[7]
			server_details['osversion'] = i[8]
			server_details['ipaddress'] = i[9]
			server_details['managed'] = i[10]

		return server_details


	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()

def makelist(hlist):
	sl = str(hlist)
	nl = sl.split()
	return nl


def verifyHostname(h):

	#check for correct case
	hostname = h.lower()

	#check domain name
	if domain not in h and 'xxx-' not in hostname:
		hostname = h + domain

	return hostname

def cleanPath(results_file):
	# results_file = os.getcwd() + '/penguins/static/cmdb_result_export_' + today + '.csv'
	print(results_file)
	try:
		if os.path.isfile(results_file):
			os.remove(results_file)
		else:
			print('No previous search results')
			with open(results_file,"w+") as f:
				pass
				f.close()
	except:
		pass

#### TMC file creation
def createHeaderTMC(path):
	with open(path,'a+') as f:
		f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
			'hostname',
			'config_manager',
			'bu',
			'cost_centre',
			'company_code',
			'server_role',
			'server_type',
			'arch',
			'ostype',
			'osversion',
			'ipaddress',
			'uptime',
			'last_checkin',
			'clamav',
			'clamdb',
			'clam_update',
			'splunk',
			'tetration',
			'flexera',
			'netbackup',
			'checkmk',
			'sudo',
			'besagent',
			'ccs',
			'tmc',
			'greatwall',
			'ad_auth'))
	f.close()

def writePathTMC(server_dict, path):
	cleanPathTMC(path)
	createHeaderTMC(path)
	if isinstance(server_dict, dict):
		with open(path,'a+') as f:
			for i in server_dict:
				hostname = i							# Hostname
				config_manager = server_dict[i][0]		# Config Manager
				bu = server_dict[i][1]					# BU
				cost_centre = server_dict[i][2]			# Cost Centre
				company_code = server_dict[i][3]		# Company Code
				server_role = server_dict[i][4]			# Server Role
				server_type = server_dict[i][5]			# Server type
				arch = server_dict[i][6]				# Arcitecture
				ostype = server_dict[i][7]				# OS
				osversion = server_dict[i][8]			# OS version
				ipaddress = server_dict[i][9]			# IP address
				uptime = server_dict[i][10]				# uptime
				last_checking = server_dict[i][11]		# Last Check in
				clamav = server_dict[i][12]				# ClamAV
				clamdb = server_dict[i][13]				# ClamDB
				clam_update = server_dict[i][14]		# Clam update
				splunk = server_dict[i][15]				# Splunk
				tetration = server_dict[i][16]			# Tetration
				flexera = server_dict[i][17]			# Flexera
				netbackup = server_dict[i][18]			# Netbackup
				checkmk = server_dict[i][19]			# CheckMK
				sudo = server_dict[i][20]				# sudo
				besagent = server_dict[i][21]			# BESAgent
				ccs = server_dict[i][22]				# ccs
				tmc = server_dict[i][23]				# tmc
				greatwall = server_dict[i][24]			# greatwall
				ad_auth = server_dict[i][25]			# ad_auth

				f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
					hostname,
					config_manager,
					bu,
					cost_centre,
					company_code,
					server_role,
					server_type,
					arch,
					ostype,
					osversion,
					ipaddress,
					uptime,
					last_checkin,
					clamav,
					clamdb,
					clam_update,
					splunk,
					tetration,
					flexera,
					netbackup,
					checkmk,
					sudo,
					besagent,
					ccs,
					tmc,
					greatwall,
					ad_auth))

	elif isinstance(server_dict,list):
		print("The instance is a list")
		for server in server_dict:
			with open(path,'a+') as f:
				# print(server)
				#print(type(server))
				hostname = server['hostname']
				config_manager = server['config_manager']
				bu = server['bu']
				cost_centre = server['cost_centre']
				company_code = server['company_code']
				server_role = server['server_role']
				server_type = server['server_type']
				arch = server['arch']
				ostype = server['ostype']
				osversion = server['osversion']
				ipaddress = server['ipaddress']
				uptime = server['uptime']
				last_checkin = server['last_checkin']
				clamav = server['clamav']
				clamdb = server['clamdb']
				clam_update = server['clam_update']
				splunk = server['splunk']
				tetration = server['tetration']
				flexera = server['flexera']
				netbackup = server['netbackup']
				checkmk = server['checkmk']
				sudo = server['sudo']
				besagent = server['besagent']
				ccs = server['ccs']
				tmc = server['tmc']
				greatwall = server['greatwall']
				ad_auth = server['ad_auth']

				f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
					hostname,
					config_manager,
					bu,
					cost_centre,
					company_code,
					server_role,
					server_type,
					arch,
					ostype,
					osversion,
					ipaddress,
					uptime,
					last_checkin,
					clamav,
					clamdb,
					clam_update,
					splunk,
					tetration,
					flexera,
					netbackup,
					checkmk,
					sudo,
					besagent,
					ccs,
					tmc,
					greatwall,
					ad_auth))

def cleanPathTMC(path):
	try:
		if os.path.isfile(path):
			os.remove(path)
		else:
			print('No previous search results')
			with open(path,"w+") as f:
				pass
				f.close()
	except:
		pass

######################################################

def createHeader():
	results_file = os.getcwd() + '/penguins/static/cmdb_result_export-' + today + '.csv'
	with open(results_file,'a+') as f:
		f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format('hostname','bu','cost_centre','company_code','role','vm_type','arch','ostype','osversion','ipaddress','managed'))

def writePath(server_dict,path):
	cleanPath(path)
	results_file = path
	createHeader()
	if isinstance(server_dict, dict):
		with open(results_file,'a+') as f:
			for i in server_dict:
				hostname = i
				bu = server_dict[i][0]
				cost_centre = server_dict[i][1]
				company_code = server_dict[i][2]
				role = server_dict[i][3]
				vm_type = server_dict[i][4]
				arch = server_dict[i][5]
				ostype = server_dict[i][6]
				osversion = server_dict[i][7]
				ipaddress = server_dict[i][8]
				managed = server_dict[i][9]
				print("{},{},{},{},{},{},{},{},{},{},{}\n".format(hostname,bu,cost_centre,company_code,role,vm_type,arch,ostype,osversion,ipaddress,managed))
				f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(hostname,bu,cost_centre,company_code,role,vm_type,arch,ostype,osversion,ipaddress,managed))
	elif isinstance(server_dict,list):
		print("The instance is a list")
		for server in server_dict:
			with open(results_file,'a+') as f:
				# print(server)
				hostname = server['host_name']
				bu = server['BU']
				cost_centre = server['Cost_Centre']
				company_code = server['Company_Code']
				role = server['role']
				vm_type = server['host_type']
				arch = server['architecture']
				ostype = server['osfamily']
				osversion = server['osversion']
				ipaddress = server['ipaddress']
				managed = server['managed']
				print("{},{},{},{},{},{},{},{},{},{},{}\n".format(hostname,bu,cost_centre,company_code,role,vm_type,arch,ostype,osversion,ipaddress,managed))
				f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(hostname,bu,cost_centre,company_code,role,vm_type,arch,ostype,osversion,ipaddress,managed))


### Functions and Classes for the Patch Check page
# functions and classes
def queryDB(database,table,searchQuery):
	server_details = defaultdict(list)
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database=database)

		cursor = connection.cursor()
		searchQuery =  searchQuery
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		for i in output:
			server_details[i[0]].append(i[1])
			server_details[i[0]].append(i[2])
			server_details[i[0]].append(i[3])
			server_details[i[0]].append(i[4])
			server_details[i[0]].append(i[5])
			server_details[i[0]].append(i[6])
			server_details[i[0]].append(i[7])
			server_details[i[0]].append(i[8])
			server_details[i[0]].append(i[9])
		return server_details

	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()

def queryDB_fact(database,table,searchQuery):
	server_details = defaultdict(list)
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		connection = psycopg2.connect(user = "postgres",
									password = password,
									host="x.x.x.x",
									port="5432",
									database=database)


		cursor = connection.cursor()
		searchQuery =  searchQuery
		cursor.execute(searchQuery)
		output = cursor.fetchall()
		return output

	except (Exception, psycopg2.error) as e:
		print("Error while connecting to DB", str(e))

	finally:
		if connection:
			cursor.close()
			connection.close()


def getfactvalues(fact_type,table):
	fact_list = []
	search_column = "select {} from {};".format(fact_type,table)
	column_lookup = queryDB_fact(database,table,search_column)
	for i in column_lookup:
		if i[0] not in fact_list:
			fact_list.append(i[0])
	return fact_list

def byfact(table,column,fact):
	count = 0
	searchfact = "select * from {} where {} = '{}';".format(table,column,fact)
	fdict = {}
	fact_lookup = queryDB(database,table,searchfact)
	for i in fact_lookup:
		count += 1
	fdict[fact] = count
	return fdict


def generate_current_results(host_entries):
	results = os.getcwd() + '/penguins/static/current_patch_results.csv'
	try:
		if os.path.exists(results):
			os.remove(results)
			print("removing old file")
		else:
			pass
	except:
		print("Error in patch file creation. Exiting")

	with open(results,'a+') as f:
		f.write('{},{},{},{},{},{},{},{},{},{}\n'.format('hostname', 'virt_type', 'capsule','errata_status','subscription_status','virtual_host','kernel version','os family','os release','uptime_days'))
		f.close()

	with open(results,'a+') as f:
		for h in host_entries:
			f.write('{},{},{},{},{},{},{},{},{},{}\n'.format(h,host_entries[h][0],host_entries[h][1],host_entries[h][2],host_entries[h][3],host_entries[h][4],host_entries[h][5],host_entries[h][6],host_entries[h][7],host_entries[h][8]))


def getDBConn(dbName):
	conn = None
	connConnected = False
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		conn = psycopg2.connect(user = "postgres",
								password = password,
								host = "x.x.x.x",
								port = "5432",
								database = dbName)

		cursor = conn.cursor()
		cursor.execute("SELECT version();")
		record = cursor.fetchone()
		if record:
			print("successfully connected to DB:", dbName)
			connConnected = True
		else:
			connConnected = False

	except (Exception, psycopg2.Error) as error :
		print("Error while connecting to PostgreSQL", error)

	finally:
		# closing database cursor connection.
		if(conn):
			cursor.close()

	return conn


def dbQueryExecutor(dbName, dbQuery):
	foundSelectResults = dict()
	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		conn = psycopg2.connect(user = "postgres",
								password = password,
								host = "x.x.x.x",
								port = "5432",
								database = dbName)
		cursor = conn.cursor()
		cursor.execute(dbQuery)
		conn.commit()

		# message to be displayed to user on live messages page
		liveMessage = "db query ran successfully"
		print(liveMessage)
		print()
		general.showUserMessage(liveMessage)

		if "SELECT *" in dbQuery and dbName == "decommission" and "FROM decommed_hosts" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				for row in output:
					listItems = list()

					row_id = row[0]

					date_time_actioned = str(row[1])
					listItems.append(date_time_actioned)

					change_number = str(row[2])
					listItems.append(change_number)

					host_name = str(row[3])
					listItems.append(host_name)

					puppet_decommed = str(row[4])
					listItems.append(puppet_decommed)

					chef_decommed = str(row[10])
					listItems.append(chef_decommed)

					vsphere_decommed = str(row[5])
					listItems.append(vsphere_decommed)

					satellite_decommed = str(row[6])
					listItems.append(satellite_decommed)

					physical_decommed = str(row[7])
					listItems.append(physical_decommed)

					tmc_db_decommed = str(row[9])
					listItems.append(tmc_db_decommed)

					actioned_by = str(row[8])
					listItems.append(actioned_by)

					foundSelectResults[row_id] = listItems

		if "SELECT" in dbQuery and dbName == "stack" and "FROM overflow" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				for row in output:
					listItems = list()

					row_id = row[0]

					date_time_added = str(row[1])
					listItems.append(date_time_added)

					ref_number = str(row[2])
					listItems.append(ref_number)

					purchased = str(row[3])
					listItems.append(purchased)

					valuated = str(row[4])
					listItems.append(valuated)

					cleaned = str(row[5])
					listItems.append(cleaned)

					actioned_by = str(row[6])
					listItems.append(actioned_by)

					foundSelectResults[row_id] = listItems

		if "SELECT *" in dbQuery and dbName == "linux_cmdb" and "FROM cmdb" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				for row in output:
					listItems = list()

					hostname = row[0]

					bu = str(row[1])
					listItems.append(bu)

					cost_centre = str(row[2])
					listItems.append(cost_centre)

					company_code = str(row[3])
					listItems.append(company_code)

					role = str(row[4])
					listItems.append(role)

					host_type = str(row[5])
					listItems.append(host_type)

					architecture = str(row[6])
					listItems.append(architecture)

					osfamily = str(row[7])
					listItems.append(osfamily)

					osversion = str(row[8])
					listItems.append(osversion)

					ipaddress = str(row[9])
					listItems.append(ipaddress)

					managed = str(row[10])
					listItems.append(managed)

					foundSelectResults[hostname] = listItems

		if "SELECT *" in dbQuery and dbName == "tmc" and "FROM tmc_main" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				for row in output:
					listItems = list()

					id = [0]
					hostname = str(row[1])
					listItems.append(hostname)

					config_manager = str(row[2])
					listItems.append(config_manager)

					bu = str(row[3])
					listItems.append(bu)

					cost_centre = str(row[4])
					listItems.append(cost_centre)

					company_code = str(row[5])
					listItems.append(company_code)

					server_role = str(row[6])
					listItems.append(server_role)

					server_type = str(row[7])
					listItems.append(server_type)

					architecture = str(row[8])
					listItems.append(architecture)

					osfamily = str(row[9])
					listItems.append(osfamily)

					osversion = str(row[10])
					listItems.append(osversion)

					ipaddress = str(row[11])
					listItems.append(ipaddress)

					uptime = str(row[12])
					listItems.append(uptime)

					last_checkin = str(row[13])
					listItems.append(last_checkin)

					clamav = str(row[14])
					listItems.append(clamav)

					clamdb = str(row[15])
					listItems.append(clamdb)

					clam_update = str(row[16])
					listItems.append(clam_update)

					splunk = str(row[17])
					listItems.append(splunk)

					tetration = str(row[18])
					listItems.append(tetration)

					flexera = str(row[19])
					listItems.append(flexera)

					netbackup = str(row[20])
					listItems.append(netbackup)

					checkmk = str(row[21])
					listItems.append(checkmk)

					sudo = str(row[22])
					listItems.append(sudo)

					besagent = str(row[23])
					listItems.append(besagent)

					ccs = str(row[24])
					listItems.append(ccs)

					tmc = str(row[28])
					listItems.append(tmc)

					greatwall = str(row[25])
					listItems.append(greatwall)

					ad_auth = str(row[26])
					listItems.append(ad_auth)

					splunk_id = row[27]

					foundSelectResults[hostname] = listItems

		if "SELECT" in dbQuery and dbName == "tmc" and "SELECT config_manager, COUNT(config_manager)" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				listConfigManagers = list()
				listNumManaged = list()
				dictItems = dict()
				for row in output:
					configManager = row[0]
					listConfigManagers.append(configManager)
					dictItems['config_managers'] = listConfigManagers

					numHostsManaged = row[1]
					listNumManaged.append(numHostsManaged)
					dictItems['num_managed'] = listNumManaged

				foundSelectResults = dictItems

		if "SELECT" in dbQuery and dbName == "tmc" and "SELECT bu, COUNT(bu)" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				listBUs = list()
				listNumBUs = list()
				dictItems = dict()
				for row in output:
					bu = row[0]
					listBUs.append(bu)
					dictItems['bu_s'] = listBUs

					numBUs = row[1]
					listNumBUs.append(numBUs)
					dictItems['num_bu_s'] = listNumBUs

				foundSelectResults = dictItems

		if "SELECT" in dbQuery and dbName == "tmc" and "SELECT role, COUNT(role)" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				listEnvs = list()
				listNumEnvs = list()
				dictItems = dict()
				for row in output:
					env = row[0]
					listEnvs.append(env)
					dictItems['env_s'] = listEnvs

					numEnvs = row[1]
					listNumEnvs.append(numEnvs)
					dictItems['num_env_s'] = listNumEnvs

				foundSelectResults = dictItems

		if "SELECT" in dbQuery and dbName == "tmc" and "SELECT host_type, COUNT(host_type)" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				listServerTypes = list()
				listNumServerTypes = list()
				dictItems = dict()
				for row in output:
					serverType = row[0]
					listServerTypes.append(serverType)
					dictItems['server_types'] = listServerTypes

					numServerTypes = row[1]
					listNumServerTypes.append(numServerTypes)
					dictItems['num_server_types'] = listNumServerTypes

				foundSelectResults = dictItems

		if "SELECT" in dbQuery and dbName == "tmc" and "SELECT greatwall, COUNT(greatwall)" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				listGreatwall = list()
				listNumGreatwall = list()
				dictItems = dict()
				for row in output:
					greatwall = row[0]
					if greatwall == True:
						greatwall = "enabled"
					elif greatwall == False:
						greatwall = "disabled"

					listGreatwall.append(greatwall)
					dictItems['greatwall_s'] = listGreatwall

					numGreatwall = row[1]
					listNumGreatwall.append(numGreatwall)
					dictItems['num_greatwall_s'] = listNumGreatwall

				foundSelectResults = dictItems

		if "SELECT" in dbQuery and dbName == "tmc" and "SELECT ad_auth, COUNT(ad_auth)" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				listADAuth = list()
				listNumADAuth = list()
				dictItems = dict()
				for row in output:
					adAuth = row[0]
					if adAuth == True:
						adAuth = "enabled"
					elif adAuth == False:
						adAuth = "disabled"

					listADAuth.append(adAuth)
					dictItems['ad_auth_s'] = listADAuth

					numADAuth = row[1]
					listNumADAuth.append(numADAuth)
					dictItems['num_ad_auth_s'] = listNumADAuth

				foundSelectResults = dictItems

		if "SELECT" in dbQuery and dbName == "tmc" and "SELECT DISTINCT osfamily" in dbQuery:
			output = cursor.fetchall()

			if len(output) > 0:
				listOSFamiliesAll = list()
				listOSFamiliesLower = list()
				listOSFamilies = list()
				dictItems = dict()
				for row in output:
					osFamily = row[0]
					listOSFamiliesAll.append(osFamily)

				for item in listOSFamiliesAll:
					osFamilyLower = item.lower()
					listOSFamiliesLower.append(osFamilyLower)

				for item in listOSFamiliesLower:
					if item not in listOSFamilies:
						listOSFamilies.append(item)

				for osFamily in listOSFamilies:
					dictOSFamiliesCount = dict()
					countOSFamiliesQuery = "SELECT osversion, COUNT(osversion) AS osversion_count \
											FROM tmc_main WHERE LOWER(osfamily) = \
											LOWER('{}') GROUP BY osversion;".format(
											osFamily
											)

					cursor.execute(countOSFamiliesQuery)
					conn.commit()
					output = cursor.fetchall()

					for row in output:
						osVersion = row[0]
						osVersionCount = row[1]
						dictOSFamiliesCount[osVersion] = osVersionCount

					if 'centos' in osFamily:
						osFamily = "centos"

					dictItems[osFamily] = dictOSFamiliesCount

				foundSelectResults = dictItems

		if "SELECT" in dbQuery and dbName == "tmc" and "column_name from information_schema.columns" in dbQuery and "splunk_status" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				listItems = list()
				for row in output:
					listItems.append(row[0])
					row_id = 1
					foundSelectResults[row_id] = listItems

		if "SELECT" in dbQuery and dbName == "tmc" and "INNER JOIN splunk_status" in dbQuery and "splunk_id" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				for row in output:
					listItems = list()

					row_id = row[0]

					hostname = str(row[1])
					listItems.append(hostname)

					splunk_status_id = row[2]

					managed = row[3]
					listItems.append(managed)

					self_managed = row[4]
					listItems.append(self_managed)

					installed = row[5]
					listItems.append(installed)

					latest_installed = row[6]
					listItems.append(latest_installed)

					version_installed = str(row[7])
					listItems.append(version_installed)

					running = row[8]
					listItems.append(running)

					handshake = row[9]
					listItems.append(handshake)

					varlog_access = row[10]
					listItems.append(varlog_access)

					varlog_messages_access = row[11]
					listItems.append(varlog_messages_access)

					varlog_secure_access = row[12]
					listItems.append(varlog_secure_access)

					os_logs_populated = row[13]
					listItems.append(os_logs_populated)

					frg_conf_dir_exists = row[14]
					listItems.append(frg_conf_dir_exists)

					foundSelectResults[row_id] = listItems

		if "SELECT" in dbQuery and dbName == "tmc" and "column_name from information_schema.columns" in dbQuery and "flexera_status" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				listItems = list()
				for row in output:
					listItems.append(row[0])
					row_id = 1
					foundSelectResults[row_id] = listItems

		if "SELECT" in dbQuery and dbName == "tmc" and "INNER JOIN flexera_status" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				for row in output:
					listItems = list()

					row_id = row[0]

					hostname = str(row[1])
					listItems.append(hostname)

					running = row[3]
					listItems.append(running)

					installed = row[4]
					listItems.append(installed)

					installed_version = row[5]
					listItems.append(installed_version)

					policy_file = row[6]
					listItems.append(policy_file)

					upload_file = row[7]
					listItems.append(upload_file)

					tracker_file = row[8]
					listItems.append(tracker_file)

					beacon = row[9]
					listItems.append(beacon)

					foundSelectResults[row_id] = listItems

		if "SELECT COUNT(id) AS Total" in dbQuery and dbName == "decommission" and "FROM decommed_hosts" in dbQuery:
			output = cursor.fetchall()
			if len(output) > 0:
				for row in output:
					total = row[0]
					foundSelectResults[1] = total

	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while connecting to DB: '{}'".format(dbName)
		print(error)
		print()
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(e)
		general.showUserMessage(str(e))
		general.showUserMessage(".")

	finally:
		# closing database cursor connection.
		if(conn):
			cursor.close()
			conn.close()
			# message to be displayed to user on live messages page
			liveMessage = "successfully disconnected from DB:".format(dbName)
			print(liveMessage)
			print()
			general.showUserMessage(liveMessage)

	return foundSelectResults

def dbMultiQueryExecutor(dbName, dbTable, list, queryType):
	foundSelectResults = dict()

	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		conn = psycopg2.connect(user = "postgres",
								password = password,
								host = "x.x.x.x",
								port = "5432",
								database = dbName)
		cursor = conn.cursor()

		if queryType == "agent_count":
			dictItems = dict()
			for agent in list:
				dictAgentVersionCount = dict()
				if agent == "clamav_version":
					dbQuery = "SELECT regexp_replace({}, E'[\\n\\r]+', '', 'g'), \
								count({}) AS {}_count FROM {} GROUP BY {};".format(
																		agent,
																		agent,
																		agent,
																		dbTable,
																		agent
																		)
				else:
					dbQuery = "SELECT {}, count({}) AS {}_count FROM {} \
								GROUP BY {};".format(	agent,
														agent,
														agent,
														dbTable,
														agent
														)
				cursor.execute(dbQuery)
				conn.commit()
				output = cursor.fetchall()

				if len(output) > 0:
					for row in output:
						try:
							if row[0] != None:
								agentVersion = row[0].strip()
							else:
								agentVersion = row[0]

							agentVersionCount = row[1]
							dictAgentVersionCountKeys = [*dictAgentVersionCount]

							if agentVersion in dictAgentVersionCountKeys:
								existingAgentVersionCount = dictAgentVersionCount.get(agentVersion)
								agentVersionCount = int(existingAgentVersionCount) + agentVersionCount
								dictAgentVersionCount.pop(agentVersion)

							if agentVersion != None and agentVersionCount != 0:
								dictAgentVersionCount[agentVersion] = agentVersionCount

						except Exception as e:
							print("ERROR:")
							print(str(e))

					dictItems[agent] = dictAgentVersionCount


		foundSelectResults = dictItems

	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while connecting to DB: '{}'".format(dbName)
		print(error)
		print()
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(e)
		general.showUserMessage(str(e))
		general.showUserMessage(".")

	finally:
		# closing database cursor connection.
		if(conn):
			cursor.close()
			conn.close()
			# message to be displayed to user on live messages page
			liveMessage = "successfully disconnected from DB:".format(dbName)
			print(liveMessage)
			print()
			general.showUserMessage(liveMessage)

	return foundSelectResults


def dbConnDisconnect(conn):
	try:
		if(conn):
			conn.close()
			# message to be displayed to user on live messages page
			liveMessage = "successfully disconnected from DB:"
			print(liveMessage)
			print()
			general.showUserMessage(liveMessage)
	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while disconnecting from DB"
		print(error)
		print()
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(e)
		general.showUserMessage(str(e))
		general.showUserMessage(".")

def queryVsphereDB(serversList):
	inVsphereDBServersList = list()
	notInVsphereDBServersList = list()
	inVsphereDBvcsVmsDict = dict()
	dbName = "vsphere"
	dbTableName = "managed_vms"
	selectQuery = str()

	# message to be displayed to user on live messages page
	liveMessage = "Method to query DB Table: '{}' on DB: '{}' for VM's that we manage.".format(dbTableName, dbName)
	print(liveMessage)
	print()
	general.showUserMessage(liveMessage)

	conn = None
	cursor = None

	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		conn = psycopg2.connect(user = "postgres",
								password = password,
								host = "x.x.x.x",
								port = "5432",
								database = dbName)
		cursor = conn.cursor()
	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while connecting to DB: '{}'".format(dbName)
		print(error)
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(str(e))
		print()
		general.showUserMessage(str(e))
		general.showUserMessage(".")

	for server in serversList:
		vcVMsList = list()
		selectQuery = "SELECT * FROM {} WHERE {} = '{}';".format(
					dbTableName,
					"vm_name",
					server
		)
		try:
			cursor.execute(selectQuery)
			output = cursor.fetchall()
			try:
				outputList = output[0]
				outputVC = outputList[1]
				outputServer = outputList[2]
			except:
				outputServer = str()

			if server.lower() in outputServer.lower():
				# message to be displayed to user on live messages page
				liveMessage = "server: '{}' in vsphere DB".format(server)
				print(liveMessage)
				print()
				general.showUserMessage(liveMessage)

				inVsphereDBServersList.append(server)

				# setting dictionary of vc's and the vm's in each vc
				if outputVC in inVsphereDBvcsVmsDict.keys():
					vcVMsList = inVsphereDBvcsVmsDict[outputVC]
					vcVMsList.append(outputServer)
					inVsphereDBvcsVmsDict[outputVC] = vcVMsList
				else:
					vcVMsList.append(outputServer)
					inVsphereDBvcsVmsDict[outputVC] = vcVMsList

			else:
				# message to be displayed to user on live messages page
				liveMessage = "server: '{}' NOT in vsphere DB".format(server)
				print(liveMessage)
				print()
				general.showUserMessage(liveMessage)

				notInVsphereDBServersList.append(server)

		except Exception as e:
			# message to be displayed to user on live messages page
			error = "Error while querying Table '{}' on DB: '{}'".format(dbTableName, dbName)
			print(error)
			general.showUserMessage(error)

			print("Exception:")
			general.showUserMessage("Exception:")
			print(str(e))
			print()
			general.showUserMessage(str(e))
			general.showUserMessage(".")

	session['servers_in_vsphere_list'] = inVsphereDBServersList
	session['servers_not_in_vsphere_list'] = notInVsphereDBServersList
	session['vcs_vms_in_vspheredb_dict'] = inVsphereDBvcsVmsDict


def cleanupVsphereDB(server):
	dbName = "vsphere"
	dbTableName = "managed_vms"
	outputID = -1
	selectQuery = str()

	# message to be displayed to user on live messages page
	liveMessage = "Method to cleanup host/s in DB Table: '{}' on DB: '{}'.".format(
		dbTableName,
		dbName
	)
	print(liveMessage)
	print()
	general.showUserMessage(liveMessage)

	conn = None
	cursor = None

	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		conn = psycopg2.connect(user = "postgres",
								password = password,
								host = "x.x.x.x",
								port = "5432",
								database = dbName)
		cursor = conn.cursor()
	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while connecting to DB: '{}'".format(dbName)
		print(error)
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(str(e))
		print()
		general.showUserMessage(str(e))
		general.showUserMessage(".")

	selectQuery = "SELECT id FROM {} WHERE LOWER({}) LIKE LOWER('%{}%');".format(
				dbTableName,
				"vm_name",
				server
	)
	try:
		cursor.execute(selectQuery)
		output = cursor.fetchall()
		try:
			outputList = output[0]
			outputID = outputList[0]
		except:
			outputID = -1

		if outputID != -1:
			# message to be displayed to user on live messages page
			liveMessage = "cleaning up server: '{}' in DB: '{}'".format(server, dbName)
			print(liveMessage)
			print()
			general.showUserMessage(liveMessage)

			deleteQuery = "DELETE FROM {} WHERE {} = {};".format(dbTableName, 'id', outputID)

			try:
				cursor.execute(deleteQuery)
				rowsDeleted = cursor.rowcount
				print("rows deleted: '{}'".format(rowsDeleted))
				# commit delete/s to DB
				conn.commit()
			except:
				error = "Error while running delete query: '{}' on DB: '{}'".format(deleteQuery, dbName)
				print(error)
				general.showUserMessage(error)

		else:
			# message to be displayed to user on live messages page
			liveMessage = "server: '{}' NOT in DB: '{}'".format(server, dbName)
			print(liveMessage)
			print()
			general.showUserMessage(liveMessage)

	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while querying Table '{}' on DB: '{}'".format(dbTableName, dbName)
		print(error)
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(str(e))
		print()
		general.showUserMessage(str(e))
		general.showUserMessage(".")

	if conn:
		cursor.close()
		conn.close()


def queryTMCDB(serversList):
	inTMCDBServersList = list()
	notInTMCDBServersList = list()
	dbName = "tmc"
	dbTableName = "tmc_main"
	selectQuery = str()
	outputID = -1

	# message to be displayed to user on live messages page
	liveMessage = "Method to query for host/s in DB Table: '{}' on DB: '{}'.".format(dbTableName, dbName)
	print(liveMessage)
	print()
	general.showUserMessage(liveMessage)

	conn = None
	cursor = None

	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		conn = psycopg2.connect(user = "postgres",
								password = password,
								host = "x.x.x.x",
								port = "5432",
								database = dbName)
		cursor = conn.cursor()
	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while connecting to DB: '{}'".format(dbName)
		print(error)
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(str(e))
		print()
		general.showUserMessage(str(e))
		general.showUserMessage(".")

	for server in serversList:
		selectQuery = "SELECT id FROM {} WHERE LOWER({}) LIKE LOWER('%{}%');".format(
					dbTableName,
					"hostname",
					server
		)
		try:
			cursor.execute(selectQuery)
			output = cursor.fetchall()
			try:
				outputList = output[0]
				outputID = outputList[0]
			except:
				outputID = -1

			if outputID != -1:
				# message to be displayed to user on live messages page
				liveMessage = "server: '{}' in {} DB".format(server, dbName)
				print(liveMessage)
				print()
				general.showUserMessage(liveMessage)

				inTMCDBServersList.append(server)
			else:
				# message to be displayed to user on live messages page
				liveMessage = "server: '{}' NOT in {} DB".format(server, dbName)
				print(liveMessage)
				print()
				general.showUserMessage(liveMessage)

				notInTMCDBServersList.append(server)

		except Exception as e:
			# message to be displayed to user on live messages page
			error = "Error while querying Table '{}' on DB: '{}'".format(dbTableName, dbName)
			print(error)
			general.showUserMessage(error)

			print("Exception:")
			general.showUserMessage("Exception:")
			print(str(e))
			print()
			general.showUserMessage(str(e))
			general.showUserMessage(".")

	session['servers_in_tmc_db_list'] = inTMCDBServersList
	session['servers_not_in_tmc_db_list'] = notInTMCDBServersList

	if conn:
		cursor.close()
		conn.close()

def cleanupTMCDB(server):
	dbName = "tmc"
	tmcDBTableName = "tmc_main"
	splunkTMCDBTableName = "splunk_status"
	flexeraTMCDBTableName = "flexera_status"
	selectQuery = str()
	outputID = -1

	# message to be displayed to user on live messages page
	liveMessage = "Method to cleanup host/s in DB Tables: '{}', '{}', '{}' on DB: '{}'.".format(
		tmcDBTableName,
		splunkTMCDBTableName,
		flexeraTMCDBTableName,
		dbName
	)
	print(liveMessage)
	print()
	general.showUserMessage(liveMessage)

	conn = None
	cursor = None

	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		conn = psycopg2.connect(user = "postgres",
								password = password,
								host = "x.x.x.x",
								port = "5432",
								database = dbName)
		cursor = conn.cursor()
	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while connecting to DB: '{}'".format(dbName)
		print(error)
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(str(e))
		print()
		general.showUserMessage(str(e))
		general.showUserMessage(".")

	selectQuery = "SELECT id FROM {} WHERE LOWER({}) LIKE LOWER('%{}%');".format(
				tmcDBTableName,
				"hostname",
				server
	)
	try:
		cursor.execute(selectQuery)
		output = cursor.fetchall()
		try:
			outputList = output[0]
			outputID = outputList[0]
		except:
			outputID = -1

		if outputID != -1:
			# message to be displayed to user on live messages page
			liveMessage = "cleaning up server: '{}' in DB: '{}'".format(server, dbName)
			print(liveMessage)
			print()
			general.showUserMessage(liveMessage)

			tmcDeleteQuery = "DELETE FROM {} WHERE {} = {};".format(tmcDBTableName, 'id', outputID)
			splunkTMCDeleteQuerty = "DELETE FROM {} WHERE {} = {};".format(splunkTMCDBTableName, 'id', outputID)
			flexeraTMCDeleteQuerty = "DELETE FROM {} WHERE {} = {};".format(flexeraTMCDBTableName, 'id', outputID)

			try:
				cursor.execute(tmcDeleteQuery)
				rowsDeleted = cursor.rowcount
				print("rows deleted: '{}'".format(rowsDeleted))
				# commit delete/s to DB
				conn.commit()
			except:
				error = "Error while running delete query: '{}' on DB: '{}'".format(tmcDeleteQuery, dbName)
				print(error)
				general.showUserMessage(error)

			try:
				cursor.execute(splunkTMCDeleteQuerty)
				rowsDeleted = cursor.rowcount
				print("rows deleted: '{}'".format(rowsDeleted))
				# commit delete/s to DB
				conn.commit()
			except:
				error = "Error while running delete query: '{}' on DB: '{}'".format(splunkTMCDeleteQuerty, dbName)
				print(error)
				general.showUserMessage(error)

			try:
				cursor.execute(flexeraTMCDeleteQuerty)
				rowsDeleted = cursor.rowcount
				print("rows deleted: '{}'".format(rowsDeleted))
				# commit delete/s to DB
				conn.commit()
			except:
				error = "Error while running delete query: '{}' on DB: '{}'".format(flexeraTMCDeleteQuerty, dbName)
				print(error)
				general.showUserMessage(error)

		else:
			# message to be displayed to user on live messages page
			liveMessage = "server: '{}' NOT in DB: '{}'".format(server, dbName)
			print(liveMessage)
			print()
			general.showUserMessage(liveMessage)

	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while querying Tables: '{}', '{}', '{}' on DB: '{}'".format(tmcDBTableName, splunkTMCDBTableName, flexeraTMCDBTableName, dbName)
		print(error)
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(str(e))
		print()
		general.showUserMessage(str(e))
		general.showUserMessage(".")

	if conn:
		cursor.close()
		conn.close()

def verifyTMCDBDecomm(server):
	dbName = "tmc"
	dbTableName = "tmc_main"
	selectQuery = str()
	conn = None
	cursor = None
	activeStatus = "Currently active"
	deactivatedStatus = "Deactivated"
	tmcDBDecommStatus = str()
	outputID = -1

	# message to be displayed to user on live messages page
	liveMessage = "Verfiy that Server has been Removed out of TMC DB Clean-up Method..."
	print(liveMessage)
	print()
	general.showUserMessage(liveMessage)

	try:
		try:
			password = anton.getTheIngredients(recipe).decode()
		except Exception as e:
			password = None
			print("Error while obtaining the necessary ingredients for the recipe.")
			print("Exception caught: '{}'".format(e))

		conn = psycopg2.connect(user = "postgres",
								password = password,
								host = "x.x.x.x",
								port = "5432",
								database = dbName)
		cursor = conn.cursor()
	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while connecting to DB: '{}'".format(dbName)
		print(error)
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(str(e))
		print()
		general.showUserMessage(str(e))
		general.showUserMessage(".")

	selectQuery = "SELECT id FROM {} WHERE LOWER({}) LIKE LOWER('%{}%');".format(
				dbTableName,
				"hostname",
				server
	)
	try:
		cursor.execute(selectQuery)
		output = cursor.fetchall()
		try:
			outputList = output[0]
			outputID = outputList[0]
		except:
			outputID = -1

		if outputID != -1:
			# message to be displayed to user on live messages page
			liveMessage = "server: '{}' in {} DB".format(server, dbName)
			print(liveMessage)
			print()
			general.showUserMessage(liveMessage)

			tmcDBDecommStatus = activeStatus

		else:
			# message to be displayed to user on live messages page
			liveMessage = "server: '{}' NOT in {} DB".format(server, dbName)
			print(liveMessage)
			print()
			general.showUserMessage(liveMessage)

			tmcDBDecommStatus = deactivatedStatus

	except Exception as e:
		# message to be displayed to user on live messages page
		error = "Error while querying Table '{}' on DB: '{}'".format(dbTableName, dbName)
		print(error)
		general.showUserMessage(error)

		print("Exception:")
		general.showUserMessage("Exception:")
		print(str(e))
		print()
		general.showUserMessage(str(e))
		general.showUserMessage(".")

	if conn:
		cursor.close()
		conn.close()

	return tmcDBDecommStatus

def createDecommHeaders(path):
	with open(path, 'w+') as f:
		f.write("date_time_actioned,change_number,host_name,puppet_decommed,chef_decommed,vsphere_decommed,satellite_decommed,physical_decommed,tmc_db_decommed,actioned_by")
		f.write("\n")
	f.close()

def writeDecommFile(path, dictionary_obj):
	with open(path, 'a+') as f:
		for k,v in dictionary_obj.items():
			date = v[0]
			CO = v[1]
			hostname = v[2]
			puppet_decommed = v[3]
			chef_decommed = v[4]
			vsphere_decommed = v[5]
			satellite_decommed = v[6]
			physical_decommed = v[7]
			tmc_db_decommed = v[8]
			actioned_by = v[9]
			f.write(f"{date},{CO},{hostname},{puppet_decommed},{chef_decommed},{vsphere_decommed},{satellite_decommed},{physical_decommed},{tmc_db_decommed},{actioned_by}\n")

def createAgentHealthHeaders(agent, path):
	if agent.lower() == 'splunk':
		columnNames = "hostname,managed,self_managed,installed,latest_installed,version_installed,running,handshake,varlog_acl_access,varlog_messages_acl_access,varlog_secure_acl_access,os_logs_populated,frg_all_deploymentclient_dir_exists"
	elif agent.lower() == 'flexera':
		columnNames = "hostname,running,installed,installed_version,policy_file,upload_file,tracker_file,beacon"
	with open(path, 'w+') as f:
		f.write(columnNames)
		f.write("\n")
	f.close()

def writeAgentHealthFile(agent, path, dictionary_obj):
	if agent.lower() == 'splunk':
		with open(path, 'a+') as f:
			for k,v in dictionary_obj.items():
				hostname = v[0]
				managed = v[1]
				self_managed = v[2]
				installed = v[3]
				latest_installed = v[4]
				version_installed = v[5]
				running = v[6]
				handshake = v[7]
				varlog_acl_access = v[8]
				varlog_messages_acl_access = v[9]
				varlog_secure_acl_access = v[10]
				os_logs_populated = v[11]
				frg_all_deploymentclient_dir_exists = v[12]
				f.write(f"{hostname},{managed},{self_managed},{installed},{latest_installed},{version_installed},{running},{handshake},{varlog_acl_access},{varlog_messages_acl_access},{varlog_secure_acl_access},{os_logs_populated},{frg_all_deploymentclient_dir_exists}\n")

	elif agent.lower() == 'flexera':
		with open(path, 'a+') as f:
			for k,v in dictionary_obj.items():
				hostname = v[0]
				running = v[1]
				installed = v[2]
				installed_version = v[3]
				policy_file = v[4]
				upload_file = v[5]
				tracker_file = v[6]
				beacon = v[7]
				f.write(f"{hostname},{running},{installed},{installed_version},{policy_file},{upload_file},{tracker_file},{beacon}\n")
