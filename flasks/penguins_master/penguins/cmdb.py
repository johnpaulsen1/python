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
from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file
)
from werkzeug.exceptions import abort
from penguins.auth import logout
from penguins.flaskdb import common_functions
from penguins.other_utils import general


dbName = "linux_cmdb"
dbTableName = "cmdb"

### Webpages
bp = Blueprint('cmdb', __name__, url_prefix='/penguins')
# options
@bp.route('/cmdb', methods=('GET', 'POST'))
def cmdb():
	global fact
	try:
		adminAccess = session.get('admin_access')
	except:
		adminAccess = False
	try:
		cmdbAccess = session.get('cmdb_access')
	except:
		cmdbAccess = False

	### Check if user is logged in, if not redirect to login page.
	if not session.get('logged_in'):
		return redirect(url_for('login'))

	if adminAccess or cmdbAccess:
		accessGranted = True
	else:
		accessGranted = False

	if not accessGranted:
		error = "you have not been permitted to access that. Please engage with the admins if require this access."
		session['flash_errors'] = error
		return redirect(url_for('main_options'))

	if request.method == 'POST':
		if request.form['submit_button'] == 'Log Out':
			logout()
			return redirect(url_for('login'))
		elif request.form['submit_button'] == 'Back':
			return redirect(url_for('main_options'))
		elif request.form['submit_button'] == 'Show Current':
			return redirect(url_for('cmdb_current'))
		elif request.form['submit_button'] == "Search":
			return redirect(url_for('input_search_info_cmdb'))
		elif request.form['submit_button'] == "Download latest":
			return redirect(url_for('download_cmdb'))
		else:
			pass
	return render_template('cmdb/cmdb.html')


@bp.route('/cmdb/current', methods=('GET', 'POST'))
def cmdb_current():

	host_count = 0
	today = datetime.today().strftime('%Y-%m-%d')

	try:
		adminAccess = session.get('admin_access')
	except:
		adminAccess = False
	try:
		cmdbAccess = session.get('cmdb_access')
	except:
		cmdbAccess = False

	### Check if user is logged in, if not redirect to login page.
	if not session.get('logged_in'):
		return redirect(url_for('login'))

	if adminAccess or cmdbAccess:
		accessGranted = True
	else:
		accessGranted = False

	if not accessGranted:
		error = "you have not been permitted to access that. Please engage with the admins if require this access."
		session['flash_errors'] = error
		return redirect(url_for('main_options'))
	# initial variables.

	if request.method == 'POST':
		if request.form['submit_button'] == 'Log Out':
			logout()
			return redirect(url_for('login'))
		elif request.form['submit_button'] == 'Back':
			return redirect(url_for('cmdb'))
	else:
		buSearchString = general.setBUSearchString()

		if buSearchString == 'ALL':
			cmdb_hosts = common_functions.getCurrentCMDB()
		else:
			searchQuery = "SELECT * FROM {} WHERE bu in ({});".format(
							dbTableName,
							buSearchString
							)
			cmdb_hosts = common_functions.getSpecficBUsData(dbName, searchQuery)

		for i in cmdb_hosts:
			host_count += 1

		return render_template('cmdb/cmdb_current.html',
								date_today=today,
								cmdbEntries=cmdb_hosts,
								hostCount=host_count,
								buNames=buSearchString
								)
	return render_template('cmdb/test.html')


@bp.route('/cmdb/search', methods=('GET','POST'))
def input_search_info_cmdb():
	visibility = "visibility_off"
	dropdownOptions = ['host_name','ipaddress','bu','cost_centre','company_code','role','host_type','architecture','osfamily','osversion','managed' ]

	try:
		adminAccess = session.get('admin_access')
	except:
		adminAccess = False
	try:
		cmdbAccess = session.get('cmdb_access')
	except:
		cmdbAccess = False

	### Check if user is logged in, if not redirect to login page.
	if not session.get('logged_in'):
		return redirect(url_for('login'))

	if adminAccess or cmdbAccess:
		accessGranted = True
	else:
		accessGranted = False

	if not accessGranted:
		error = "you have not been permitted to access that. Please engage with the admins if require this access."
		session['flash_errors'] = error
		return redirect(url_for('main_options'))

	# get drop down values
	try:
		buNamesList = common_functions.getFactfromDB(dbName,dbTableName,'bu')
	except Exception as e:
		buNamesList = list()
		print("Exception caught: '{}'".format(str(e)))

	try:
		costCentreList = common_functions.getFactfromDB(dbName,dbTableName,'cost_centre')
	except Exception as e:
		costCentreList = list()
		print("Exception caught: '{}'".format(str(e)))

	try:
		companyCodeList = common_functions.getFactfromDB(dbName,dbTableName,'company_code')
	except Exception as e:
		companyCodeList = list()
		print("Exception caught: '{}'".format(str(e)))

	try:
		roleList = common_functions.getFactfromDB(dbName,dbTableName,'role')
	except Exception as e:
		roleList = list()
		print("Exception caught: '{}'".format(str(e)))

	try:
		hostTypeList = common_functions.getFactfromDB(dbName,dbTableName,'host_type')
	except Exception as e:
		hostTypeList = list()
		print("Exception caught: '{}'".format(str(e)))

	try:
		architectureList = common_functions.getFactfromDB(dbName,dbTableName,'architecture')
	except Exception as e:
		architectureList = list()
		print("Exception caught: '{}'".format(str(e)))

	try:
		osfamilyList = common_functions.getFactfromDB(dbName,dbTableName,'osfamily')
	except Exception as e:
		osfamilyList = list()
		print("Exception caught: '{}'".format(str(e)))

	try:
		osversionList = common_functions.getFactfromDB(dbName,dbTableName,'osversion')
	except Exception as e:
		osversionList = list()
		print("Exception caught: '{}'".format(str(e)))

	try:
		managedList = common_functions.getFactfromDB(dbName,dbTableName,'managed')
	except Exception as e:
		managedList = list()
		print("Exception caught: '{}'".format(str(e)))

	if request.method == 'POST':
		if request.form['submit_button'] == 'Log Out':
			logout()
			return redirect(url_for('login'))
		elif request.form['submit_button'] == 'Back':
			return redirect(url_for('cmdb'))
		elif request.form['submit_button'] == 'Search':
			search_option = request.form['cmdb_search_by']
			cmdbSearchField = request.form['cmdb_search_field']
			searchColumn = str()
			fieldToSearch = str()
			cmdbHostnamesList = list()
			cmdbIPAdressesList = list()

			if search_option == "host_name":
				searchColumn = search_option
				cmdbHostnames = cmdbSearchField
				cmdbHostnamesList = cmdbHostnames.split()
				if len(cmdbHostnamesList) > 0:
					i = 0
					for server in cmdbHostnamesList:
						if i == 0:
							fieldToSearch = server
						if i > 0:
							fieldToSearch = fieldToSearch + "|" + server
						i += 1
					headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "ipaddress":
				searchColumn = search_option
				cmdbIPAdresses = cmdbSearchField
				cmdbIPAdressesList = cmdbIPAdresses.split()
				if len(cmdbIPAdressesList) > 0:
					i = 0
					for ipaddress in cmdbIPAdressesList:
						if i == 0:
							fieldToSearch = ipaddress
						if i > 0:
							fieldToSearch = fieldToSearch + "|" + ipaddress
						i += 1
					headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "bu":
				searchColumn = search_option
				selected_search_option = request.form['bu_name_selection']
				fieldToSearch = selected_search_option
				headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "cost_centre":
				searchColumn = search_option
				selected_search_option = request.form['cost_centre_selection']
				fieldToSearch = selected_search_option
				headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "company_code":
				searchColumn = search_option
				selected_search_option = request.form['company_code_selection']
				fieldToSearch = selected_search_option
				headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "role":
				searchColumn = search_option
				selected_search_option = request.form['role_selection']
				fieldToSearch = selected_search_option
				headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "host_type":
				searchColumn = search_option
				selected_search_option = request.form['host_type_selection']
				fieldToSearch = selected_search_option
				headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "host_type":
				searchColumn = search_option
				selected_search_option = request.form['host_type_selection']
				fieldToSearch = selected_search_option
				headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "architecture":
				searchColumn = search_option
				selected_search_option = request.form['architecture_selection']
				fieldToSearch = selected_search_option
				headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "osfamily":
				searchColumn = search_option
				selected_search_option = request.form['osfamily_selection']
				fieldToSearch = selected_search_option
				headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "osversion":
				searchColumn = search_option
				selected_search_option = request.form['osversion_selection']
				fieldToSearch = selected_search_option
				headingValue = "CMDB search by: {}".format(search_option)

			elif search_option == "managed":
				searchColumn = search_option
				selected_search_option = request.form['managed_selection']
				fieldToSearch = selected_search_option
				headingValue = "CMDB search by: {}".format(search_option)

			session['display_cmdb_heading_value'] = headingValue

			if search_option == "host_name" or search_option == "ipaddress":
				if len(cmdbHostnamesList) > 0 or len(cmdbIPAdressesList) > 0:
					selectQuery = "SELECT * FROM {} WHERE {} SIMILAR TO '%({})%';".format(
									dbTableName,
									searchColumn,
									fieldToSearch
									)
				elif len(cmdbHostnamesList) == 1 or len(cmdbIPAdressesList) == 1:
					selectQuery = "SELECT * FROM {} WHERE {} LIKE '%{}%';".format(
									dbTableName,
									searchColumn,
									fieldToSearch
									)
			else:
				selectQuery = "SELECT * FROM {} WHERE {} = '{}';".format(
								dbTableName,
								searchColumn,
								fieldToSearch
								)

			try:
				selectResults = common_functions.dbQueryExecutor(dbName, selectQuery)
				print("*" * 50)
				# print(selectResults)
			except Exception as e:
				print("error:")
				print(str(e))
			print()

			session['display_select_results_cmdb'] = selectResults
			totalRecords = len(selectResults)
			session['display_total_records_cmdb'] = totalRecords

			try:
				error = session.get('flash_errors')
			except:
				error = None

			if error is None:
				return redirect(url_for('display_search_info_cmdb'))
			elif error != None:
				flash(error)
				error = None
				session['flash_errors'] = error


		else:
			pass

	return render_template('cmdb/cmdb_search.html',
							dd_menu = dropdownOptions,
							bu_names = buNamesList,
							cost_centres = costCentreList,
							company_codes = companyCodeList,
							role_names = roleList,
							host_type_names = hostTypeList,
							architecture_names = architectureList,
							os_family_names = osfamilyList,
							os_versions = osversionList,
							managed_names = managedList
							)


@bp.route('/cmdb/display_search_info', methods=('GET', 'POST'))
def display_search_info_cmdb():
	try:
		today = datetime.today().strftime('%Y-%m-%d')
		path = os.getcwd() + '/penguins/static/cmdb_result_export-' + today + '.csv'
	except Exception as e:
		print("Exception caught: '{}'".format(str(e)))
		path = None
	try:
		headingValue = session.get('display_cmdb_heading_value')
	except:
		headingValue = None
	try:
		selectResults = session.get('display_select_results_cmdb')
	except:
		selectResults = dict()
	try:
		totalRecords = session.get('display_total_records_cmdb')
	except:
		totalRecords = 0
	try:
		error = session.get('flash_errors')
	except:
		error = None
		session['flash_errors'] = error
	try:
		adminAccess = session.get('admin_access')
	except:
		adminAccess = False
	try:
		cmdbAccess = session.get('cmdb_access')
	except:
		cmdbAccess = False

	### Check if user is logged in, if not redirect to login page.
	if not session.get('logged_in'):
		return redirect(url_for('login'))

	if adminAccess or cmdbAccess:
		accessGranted = True
	else:
		accessGranted = False

	if not accessGranted:
		error = "you have not been permitted to access that. Please engage with the admins if require this access."
		session['flash_errors'] = error
		return redirect(url_for('main_options'))

	if request.method == 'POST':
		if request.form['submit_button'] == 'Log Out':
			logout()
			return redirect(url_for('login'))
		elif request.form['submit_button'] == 'Back':
			return redirect(url_for('input_search_info_cmdb'))
		elif request.form['submit_button'] == 'Download':
			print("write to file")
			try:
				common_functions.writePath(selectResults,path)
			except Exception as e:
				print("Exception caught: '{}'".format(str(e)))

			return send_file(path, as_attachment=True)

	return render_template('cmdb/display_cmdb_results.html',
							heading_value = headingValue,
							selectResultsDict = selectResults,
							total_records = totalRecords
							)


@bp.route('/cmdb/download', methods=('GET','POST'))
def download_cmdb():
	today = datetime.today().strftime('%Y-%m-%d')
	path = os.getcwd() + '/penguins/static/cmdb_' + today + '.csv'

	try:
		adminAccess = session.get('admin_access')
	except:
		adminAccess = False
	try:
		cmdbAccess = session.get('cmdb_access')
	except:
		cmdbAccess = False

	### Check if user is logged in, if not redirect to login page.
	if not session.get('logged_in'):
		return redirect(url_for('login'))

	if adminAccess or cmdbAccess:
		accessGranted = True
	else:
		accessGranted = False

	if not accessGranted:
		error = "you have not been permitted to access that. Please engage with the admins if require this access."
		session['flash_errors'] = error
		return redirect(url_for('main_options'))
	## remove old cmdb file
	try:
		if os.path.isfile(path):
			os.remove(path)
	except:
		raise

	try:
		current_cmdb = common_functions.getCurrentCMDB()
		with open(path, 'a+') as f:
			f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format('hostname','bu','cost_centre','company_code','role','vm_type','arch','ostype','osversion','ipaddress','managed'))
		f.close()
		for i in current_cmdb:
			hostname = i
			bu = current_cmdb[i][0]
			cost_centre = current_cmdb[i][1]
			company_code = current_cmdb[i][2]
			role = current_cmdb[i][3]
			vm_type = current_cmdb[i][4]
			arch = current_cmdb[i][5]
			ostype = current_cmdb[i][6]
			osversion = current_cmdb[i][7]
			ipaddress = current_cmdb[i][8]
			managed = current_cmdb[i][9]
			with open(path,'a+') as f:
				f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(hostname,bu,cost_centre,company_code,role,vm_type,arch,ostype,osversion,ipaddress,managed))
		return send_file(path, as_attachment=True)
	except:
		return redirect(url_for('cmdb'))
