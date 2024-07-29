#!/usr/bin/python3
import functools
import io
import ast
import os
import sys
import re
import psycopg2
import datetime
from collections import defaultdict
from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file
)
from werkzeug.exceptions import abort
from penguins.auth import logout
from penguins.flaskdb import common_functions
from penguins.patch_page import patch_gen

database = "linux_cmdb"
table = "patch_main"
item = ""
column = ""
dropdownOptions = [ 'select','hostname', 'virt_type', 'capsule','errata_status','subscription_status','virtual_host','kernel version','os family','os release','uptime_days']
stats_list = [ 'virt_type', 'capsule','subscription_status','virtual_host','os family','os release']

# Search queries
search_all = "SELECT * FROM {};".format(table)
search_column = ""

path = os.getcwd() + '/penguins/static/current_patch_results.csv'

### Webpages
bp = Blueprint('patch', __name__, url_prefix='/penguins')
# options
@bp.route('/patch_page', methods=('GET', 'POST'))
def patch_page():
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
			return redirect(url_for('current_status'))
		elif request.form['submit_button'] == "Statistics":
			return redirect(url_for('patch_stats'))
		elif request.form['submit_button'] == "Search":
			return redirect(url_for('search_db'))
		elif request.form['submit_button'] == "Generate Patch Page":
			return redirect(url_for('generate_patch_page'))
		elif request.form['submit_button'] == "Download latest report":
			host_entries = common_functions.queryDB(database,table,search_all)
			common_functions.generate_current_results(host_entries)
			return send_file(path, as_attachment=True)
		else:
			pass
	return render_template('patch_page/patch_page_main.html')

@bp.route('/patch_page/current_status', methods=('GET', 'POST'))
def current_status():
	host_entries = {}
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
			return redirect(url_for('patch'))
		elif request.form['submit_button'] == 'Download':
			return send_file(path, as_attachment=True)
		else:
			pass
	host_entries = common_functions.queryDB(database,table,search_all)
	common_functions.generate_current_results(host_entries)
	return render_template('patch_page/patch_current.html',patchDBEntries=host_entries)

@bp.route('/patch_page/patch_stats', methods=('GET', 'POST'))
def patch_stats():
	fact_dict = defaultdict(list)
	x = []
	stats_list = [ 'virt_type', 'capsule','subscription_status','osfamily','lsbdistrelease']

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
			return redirect(url_for('patch'))
		else:
			pass
	for fact_type in stats_list:
		f = common_functions.getfactvalues(fact_type,table)
		for i in f:
			fact_dict[fact_type].append(byfact(table,fact_type,i))
			#print(fact_dict)
			#print(common_functions.byfact(table,fact_type,i))
	#print(fact_dict)
	for i in fact_dict.keys():
		x.append(i)
	for y in x:
		print(y)
		#print(fact_dict[y])
		for d in fact_dict[y]:
			print(d)

	return render_template('patch_page/patch_statistics.html',statList = stats_list, virtualItems=fact_dict)
	#return render_template('other/coming_soon.html')


@bp.route('/patch_page/search', methods=('GET','POST'))
def search_db():

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
			return redirect(url_for('patch'))
		elif request.form['submit_button'] == 'Search':
			if request.form['selection']:
				fact = request.form['selection']
				if fact == 'hostname':
					return redirect(url_for('search_hostname'))
				if fact == 'select':
					visibility = "visibility_on"
					error = "Please make a selection"
					return redirect(url_for('search_db'))
				else:
						fact_results = common_functions.getItemfromDB(fact, fact_search)
						common_functions.writePath(fact_results)
				return render_template('cmdb/cmdb_result_by_fact.html', cmdbHosts=fact_results)
					#  return redirect(url_for('search_patch_fact'))
		else:
			return render_template('patch_page/patch_search.html',DDmenu=dropdownOptions)
	else:
		return render_template('patch_page/patch_search.html',DDmenu=dropdownOptions)

@bp.route('/patch_page/search/hostname', methods=('GET','POST'))
def search_hostname():
	host_list = []
	host_dict = []

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
			return redirect(url_for('patch'))
		elif request.form['submit_button'] == 'Submit':
			hosts = request.form.get('Hosts')
			host_list = common_functions.makelist(hosts)
			for i in host_list:
				h = common_functions.verifyHostname(i)
				x = common_functions.getHost(h)
				host_dict.append(x)
				common_functions.writePath(host_dict,path)
			return render_template('patch_page/hostname_result.html',HostDictionaryList=host_dict)
	else:
		return render_template('patch_page/hostname_search.html')



# @bp.route('/patch_page/search/fact_search', methods=('GET','POST'))
# def search_patch_fact():
#
	# host_list = []
	# host_dict = []
#
	# try:
		# adminAccess = session.get('admin_access')
	# except:
		# adminAccess = False
	# try:
		# cmdbAccess = session.get('cmdb_access')
	# except:
		# cmdbAccess = False
#
	## Check if user is logged in, if not redirect to login page.
	# if not session.get('logged_in'):
		# return redirect(url_for('login'))
#
	# if adminAccess or cmdbAccess:
		# accessGranted = True
	# else:
		# accessGranted = False
#
	# if not accessGranted:
		# error = "you have not been permitted to access that. Please engage with the admins if require this access."
		# session['flash_errors'] = error
		# return redirect(url_for('main_options'))
#
	# if request.method == 'POST':
		# if request.form['submit_button'] == 'Log Out':
			# logout()
			# return redirect(url_for('login'))
		# elif request.form['submit_button'] == 'Back':
			# return redirect(url_for('patch'))
		# elif request.form['submit_button'] == 'Download':
			#  return send_file(path, as_attachment=True)
		# elif request.form['submit_button'] == 'Submit':
			# facts = request.form.get('facts')
			# print(facts)
			# host_list = common_functions.makelist(facts)
			# for i in host_list:
				# h = common_functions.verifyHostname(i)
				# x = common_functions.getHost(h)
				# host_dict.append(x)
				# common_functions.writePath(host_dict,path)
			# return render_template('patch_page/hostname_result.html',HostDictionaryList=host_dict)
	# else:
		# return render_template('patch_page/patch_fact_search.html')#

@bp.route('/patch_page/generate_patch_page', methods=('GET','POST'))
def generate_patch_page():

	host_list = []
	host_dict = []

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

	if adminAccess:
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
			return redirect(url_for('patch'))
		elif request.form['submit_button'] == 'Submit':
			# facts = request.form.get('facts')
			date = request.form.get('patch_date')
			change_number = request.form.get('CO')
			branch = request.form.get('branch')
			print(request.form.get('nonprod-checkbox'))
			print(request.form.get('prod-checkbox'))
			
			if request.form.get('nonprod-checkbox'):
				role = 'nonprod'

			if request.form.get('prod-checkbox'):
				role = 'prod'

			patch_gen.patch_gen(role,change_number,branch,date)
			git_url = "https://<gitlab URL>/-/merge_requests/new?merge_request%5Bsource_branch%5D=" + branch

			return render_template('patch_page/git_results.html', git_url=git_url, mr_branch=branch)
	else:
		return render_template('patch_page/git_form.html')#
