#!/usr/bin/python3
from flask import (
    Blueprint, redirect, render_template, request, session, url_for, send_file
)
from penguins.auth import logout
from penguins.agents.agent_checks import splunk, flexera
from penguins.agents import download_db_report_options

bp = Blueprint('health_check_status', __name__, url_prefix='/penguins')

splunkHealthTable = "splunk_status"
flexeraHealthTable = "flexera_status"

@bp.route('/agents/health_check_selection', methods=('GET', 'POST'))
def agents_health_check_selection():
    # variables.
    singularPageTitle = "Agent Health Check Status"

    try:
        pageTitle = session.get('page_title')
    except:
        pageTitle = "Agents Menu"

    try:
        selectedPage = session.get('selected_page')
    except:
        selectedPage = "agents_options"

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
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif selectButton == 'Back':
            return redirect(url_for('main_options'))

        elif selectButton == 'Splunk':
            selectedPage = "agents_health_check_results"
            session['selected_page'] = selectedPage
            session['page_title'] = selectButton + " - " + singularPageTitle
            updatedSelectResults = splunk.getAgentStatusData()
            session['updated_select_results'] = updatedSelectResults
            session['db_table_name'] = splunkHealthTable
            session['agent_to_health_check'] = selectButton.lower()
            return redirect(url_for(selectedPage))

        elif selectButton == 'Flexera':
            selectedPage = "agents_health_check_results"
            session['selected_page'] = selectedPage
            session['page_title'] = selectButton + " - " + singularPageTitle
            updatedSelectResults = flexera.getAgentStatusData()
            session['updated_select_results'] = updatedSelectResults
            session['db_table_name'] = flexeraHealthTable
            session['agent_to_health_check'] = selectButton.lower()
            return redirect(url_for(selectedPage))

    return render_template('agents/health_check_selection.html', title=pageTitle)



@bp.route('/agents/health_check_results', methods=('GET', 'POST'))
def agents_health_check_results():
    try:
        pageTitle = session.get('page_title')
    except:
        pageTitle = "Agents Options"

    try:
        selectedPage = session.get('selected_page')
    except:
        selectedPage = "agents_options"

    try:
        selectResults = session.get('db_select_results')
    except:
        selectResults = dict()

    try:
        agentHealthDBTable = session.get('db_table_name')
    except:
        agentHealthDBTable = str()

    try:
        agentBeingHealthChecked = session.get('agent_to_health_check')
    except:
        agentBeingHealthChecked = str()

    try:
        updatedSelectResults = session.get('updated_select_results')
    except:
        updatedSelectResults = dict()

    try:
        totalRecords = session.get('total_records')
    except:
        totalRecords = 0

    try:
        columnNames = session.get('column_names')
    except:
        columnNames = list()

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
            session['page_title'] = "Health Check Status"
            return redirect(url_for('agents_health_check_selection'))
        elif selectButton == 'Download':
            download_file = download_db_report_options.download_selected(agentBeingHealthChecked, selectResults)
            return send_file(download_file, as_attachment=True)

    return render_template('agents/health_check_results.html', title = pageTitle,
                            heading_value = pageTitle,
                            table_columns = columnNames,
                            selectResultsDict = updatedSelectResults,
                            total_records = totalRecords)
