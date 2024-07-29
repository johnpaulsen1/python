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
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    send_file, Markup
)
from werkzeug.exceptions import abort
from penguins.auth import logout
from penguins.flaskdb import common_functions
from penguins.other_utils import general

dbName = 'tmc'
dbTableName = 'tmc_main'

### Webpages
bp = Blueprint('tmc', __name__, url_prefix='/penguins')
# options
@bp.route('/tmc', methods=('GET', 'POST'))
def tmc_main():
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
        selectButton = request.form['submit_button']
        if selectButton == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif selectButton == 'Back':
            return redirect(url_for('main_options'))
        elif selectButton == 'Show Current':
            return redirect(url_for('tmc_current'))
        elif selectButton == "Search":
            return redirect(url_for('input_search_info_tmc'))
        elif selectButton == "Download latest":
            return redirect(url_for('download_tmc'))
        else:
            pass
    return render_template('tmc/tmc.html')


@bp.route('/tmc/current', methods=('GET', 'POST'))
def tmc_current():
    nr_host = 0
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
            return redirect(url_for('tmc_main'))
    else:
        buSearchString = general.setBUSearchString()

        if buSearchString == 'ALL':
            cmdb_hosts = common_functions.getCurrentTMC()
        else:
            searchQuery = "SELECT * FROM {} WHERE bu in ({});".format(
                            dbTableName,
                            buSearchString
                            )

            cmdb_hosts = common_functions.getSpecficBUsData(dbName, searchQuery)

        for i in cmdb_hosts:
            nr_host += 1

        return render_template('tmc/tmc_current.html',
                                date_today=today,
                                tmcEntries=cmdb_hosts,
                                hostCount=nr_host,
                                buNames=buSearchString
                                )
    return render_template('tmc/test.html')

@bp.route('/tmc/search', methods=('GET','POST'))
def input_search_info_tmc():
    visibility = "visibility_off"
    dropdownOptions = ['hostname','ipaddress','bu','cost_centre','company_code','role','host_type','architecture','osfamily','osversion','config_manager' ]

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
        managedList = common_functions.getFactfromDB(dbName,dbTableName,'config_manager')
    except Exception as e:
        managedList = list()
        print("Exception caught: '{}'".format(str(e)))

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('tmc_main'))
        elif request.form['submit_button'] == 'Search':
            search_option = request.form['cmdb_search_by']
            cmdbSearchField = request.form['cmdb_search_field']
            fieldToSearch = str()
            cmdbHostnamesList = list()
            cmdbIPAdressesList = list()

            if search_option == "hostname":
                cmdbHostnames = cmdbSearchField.lower()
                cmdbHostnamesList = cmdbHostnames.split()
                if len(cmdbHostnamesList) > 0:
                    i = 0
                    for server in cmdbHostnamesList:
                        if i == 0:
                            fieldToSearch = server
                        if i > 0:
                            fieldToSearch = fieldToSearch + "|" + server
                        i += 1
                    if len(cmdbHostnamesList) > 3:
                        headingValue = "TMC CMDB Search By: '{}'".format(
                                        search_option
                                        )
                    else:
                        headingValue = "TMC CMDB Search By: '{}'".format(
                                        search_option,
                                        )

            elif search_option == "ipaddress":
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

                if len(cmdbIPAdressesList) > 3:
                    headingValue = "TMC CMDB Search By: '{}'".format(
                                    search_option
                                    )
                else:
                    headingValue = "TMC CMDB Search By: '{}'".format(
                                    search_option
                                    )

            elif search_option == "bu":
                selected_search_option = request.form['bu_name_selection']
                fieldToSearch = selected_search_option
                headingValue = "TMC CMDB Search By: '{}'".format(
                                search_option
                                )

            elif search_option == "cost_centre":
                selected_search_option = request.form['cost_centre_selection']
                fieldToSearch = selected_search_option
                headingValue = "TMC CMDB Search By: '{}'".format(
                                search_option
                                )

            elif search_option == "company_code":
                selected_search_option = request.form['company_code_selection']
                fieldToSearch = selected_search_option
                headingValue = "TMC CMDB Search By: '{}'".format(
                                search_option
                                )

            elif search_option == "role":
                selected_search_option = request.form['role_selection']
                fieldToSearch = selected_search_option
                headingValue = "TMC CMDB Search By: '{}'".format(
                                search_option
                                )

            elif search_option == "host_type":
                selected_search_option = request.form['host_type_selection']
                fieldToSearch = selected_search_option
                headingValue = "TMC CMDB Search By: '{}'".format(
                                search_option
                                )

            elif search_option == "host_type":
                selected_search_option = request.form['host_type_selection']
                fieldToSearch = selected_search_option
                headingValue = "TMC CMDB Search By: '{}'".format(
                                search_option
                                )

            elif search_option == "architecture":
                selected_search_option = request.form['architecture_selection']
                fieldToSearch = selected_search_option
                headingValue = "TMC CMDB Search By: '{}'".format(
                                search_option
                                )

            elif search_option == "osfamily":
                selected_search_option = request.form['osfamily_selection']
                fieldToSearch = selected_search_option
                headingValue = "TMC CMDB Search By: '{}'".format(
                                search_option
                                )

            elif search_option == "osversion":
                selected_search_option = request.form['osversion_selection']
                fieldToSearch = selected_search_option
                headingValue = "TMC CMDB Search By: '{}'".format(
                                search_option
                                )

            elif search_option == "config_manager":
                selected_search_option = request.form['managed_selection']
                fieldToSearch = selected_search_option
                headingValue = "TMC CMDB Search By: '{}'".format(
                                search_option
                                )
            session['display_tmc_heading_value'] = headingValue

            if search_option == "hostname" or search_option == "ipaddress":
                if len(cmdbHostnamesList) > 0 or len(cmdbIPAdressesList) > 0:
                    selectQuery = "SELECT * FROM {} WHERE LOWER({}) SIMILAR TO '%({})%';".format(
                                    dbTableName,
                                    search_option,
                                    fieldToSearch
                                    )
                elif len(cmdbHostnamesList) == 1 or len(cmdbIPAdressesList) == 1:
                    selectQuery = "SELECT * FROM {} WHERE {} LIKE '%{}%';".format(
                                    dbTableName,
                                    search_option,
                                    fieldToSearch
                                    )
            else:
                selectQuery = "SELECT * FROM {} WHERE {} = '{}';".format(
                                dbTableName,
                                search_option,
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

            session['display_select_results_tmc'] = selectResults
            totalRecords = len(selectResults)
            session['display_total_records_tmc'] = totalRecords

            try:
                error = session.get('flash_errors')
            except:
                error = None

            if error is None:
                return redirect(url_for('display_search_info_tmc'))
            elif error != None:
                flash(error)
                error = None
                session['flash_errors'] = error

        else:
            pass

    return render_template('tmc/tmc_search.html',
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

@bp.route('/tmc/display_search_info', methods=('GET', 'POST'))
def display_search_info_tmc():
	try:
		today = datetime.today().strftime('%Y-%m-%d')
		path = os.getcwd() + '/penguins/static/tmc_result_export-' + today + '.csv'
	except Exception as e:
		print("Exception caught: '{}'".format(str(e)))
		path = None
	try:
		headingValue = session.get('display_tmc_heading_value')
	except:
		headingValue = None
	try:
		selectResults = session.get('display_select_results_tmc')
	except:
		selectResults = dict()
	try:
		totalRecords = session.get('display_total_records_tmc')
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
			return redirect(url_for('input_search_info_tmc'))
		elif request.form['submit_button'] == 'Download':
			print("write to file")
			try:
				common_functions.writePath(selectResults,path)
			except Exception as e:
				print("Exception caught: '{}'".format(str(e)))

			return send_file(path, as_attachment=True)

	return render_template('tmc/display_tmc_results.html',
							heading_value = headingValue,
							selectResultsDict = selectResults,
							total_records = totalRecords
							)


@bp.route('/tmc/download', methods=('GET','POST'))
def download_tmc():
    print("download button pushed")

    today = datetime.today().strftime('%Y-%m-%d')
    path = os.getcwd() + '/penguins/static/tmc_current-' + today + '.csv'

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
    #remove old tmc file
    try:
        if os.path.isfile(path):
            os.remove(path)
    except:
        raise

    try:
        with open(path, 'a+') as f:
            f.write("{},{},{},{},{},{},{},{},{},{}, \
            {},{},{},{},{},{},{},{},{},{},{},{},{}, \
            {},{},{},{}\n".format(
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
    except:
        raise
        print("File write error")

    current_tmc = common_functions.getCurrentTMC()
    for i in current_tmc:
        hostname = i
        config_manager = current_tmc[i][0]
        bu = current_tmc[i][1]
        cost_centre = current_tmc[i][2]
        company_code = current_tmc[i][3]
        server_role = current_tmc[i][4]
        server_type = current_tmc[i][5]
        arch = current_tmc[i][6]
        ostype = current_tmc[i][7]
        osversion = current_tmc[i][8]
        ipaddress = current_tmc[i][9]
        uptime = current_tmc[i][10]
        last_checkin = current_tmc[i][11]
        clamav = current_tmc[i][12].rstrip()
        clamdb = current_tmc[i][13]
        clam_update = current_tmc[i][14]
        splunk = current_tmc[i][15]
        tetration = current_tmc[i][16].rstrip()
        flexera = current_tmc[i][17].rstrip()
        netbackup = current_tmc[i][18]
        checkmk = current_tmc[i][19]
        sudo = current_tmc[i][20]
        besagent = current_tmc[i][21]
        ccs = current_tmc[i][22]
        tmc = current_tmc[i][23]
        greatwall = current_tmc[i][24]
        ad_auth = current_tmc[i][25]
        with open(path,'a+') as f:
            f.write("{},{},{},{},{},{},{},{},{},{}, \
            {},{},{},{},{},{},{},{},{},{},{},{},{}, \
            {},{},{},{}\n".format(
            hostname,
            bu,
            config_manager,
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

    return send_file(path, as_attachment=True)
