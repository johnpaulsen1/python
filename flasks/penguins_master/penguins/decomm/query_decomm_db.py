import re
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for,
    Markup, jsonify, send_file
)
from datetime import datetime, timedelta
from penguins.auth import logout, domain, userDomain
from penguins.flaskdb import common_functions
from penguins.other_utils import general
from penguins.decomm import download_decomm_db_options

bp = Blueprint('query_decomm_db', __name__, url_prefix='/penguins')
user = str()

dbName = "decommission"
dbTableName = "decommed_hosts"
selectColumnsList = ["date_time_actioned",
                    "change_number",
                    "host_name",
                    "puppet_decommed",
                    "vsphere_decommed",
                    "satellite_decommed",
                    "physical_decommed",
                    "tmc_db_decommed",
                    "actioned_by"]
cross_img_url = "/static/images/red-cross.png"
tick_img_url = "/static/images/green-tick.png"
null_img_url = "/static/images/grey-null.png"
quoteStr = "\""
startImgTag = "<img src="
endImgTag = " width=\"30\" height=\"30\"></img>"
tickEndImgTag = " width=\"34\" height=\"34\"></img>"
decommDBMenuPage = "decomm_search_db_options"
getSearchInfoPage = "input_search_info_decomm_db"

@bp.route('/decomm/search_all', methods=('GET', 'POST'))
def decomm_show_all_decomm_db():
    selectResults = dict()
    updatedSelectResults = dict()
    headingValue = "All Actioned Decommissions"
    session['display_decomm_heading_value'] = headingValue
    session['page_to_go_back_to_decomm_db_querying'] = decommDBMenuPage
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
        decommdbAccess = session.get('decommdb_access')
    except:
        decommdbAccess = False

    ### Check if user is logged in, if not redirect to login page.
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if adminAccess or decommdbAccess:
        accessGranted = True
    else:
        accessGranted = False

    if not accessGranted:
        error = "you have not been permitted to access that. Please engage with the admins if require this access."
        session['flash_errors'] = error
        return redirect(url_for('main_options'))

    user = session.get('logged_in_user')
    if domain not in user:
        user = user + userDomain

    # message to be displayed to user on live messages page
    liveMessage = "user: '{}' is on the 'All Actioned Decommissions' Report Page.".format(user)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    # if error != None:
    selectQuery = "SELECT * FROM {} ;".format(
                    dbTableName
    )

    try:
        selectResults = common_functions.dbQueryExecutor(dbName, selectQuery)
        print("*" * 50)
        print()
    except Exception as e:
        print("error:")
        print(e)

    for key, values in selectResults.items():
        img_url = str()
        valuesList = list()
        for value in values:
            if value == "N":
                value = Markup(startImgTag + quoteStr + null_img_url + quoteStr + endImgTag)
            elif value == "Y":
                value = Markup(startImgTag + quoteStr + tick_img_url + quoteStr + tickEndImgTag)
            elif value == "F":
                value = Markup(startImgTag + quoteStr + cross_img_url + quoteStr + tickEndImgTag)
            valuesList.append(value)
        updatedSelectResults[key] = valuesList

    session['display_select_results_decomm_db'] = updatedSelectResults

    totalRecords = len(updatedSelectResults)
    session['display_total_records_decomm_db'] = totalRecords

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('decomm_search_db_options'))
        elif request.form['submit_button'] == 'Download':
            decomm_download_file = download_decomm_db_options.download_selected(selectResults)
            return send_file(decomm_download_file, as_attachment=True)
        else:
            pass
    return render_template('decomm/display_decomm_db_results.html',
                            heading_value = headingValue,
                            selectResultsDict = updatedSelectResults,
                            total_records = totalRecords)


@bp.route('/decomm/input_search_info', methods=('GET', 'POST'))
def input_search_info_decomm_db():
    searchColumn = str()
    selectQuery = str()
    fromDate = str()
    toDate = str()
    selectResults = dict()
    updatedSelectResults = dict()
    headingValue = "Search Decommission DB Results"
    session['display_decomm_heading_value'] = headingValue
    session['page_to_go_back_to_decomm_db_querying'] = getSearchInfoPage
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
        decommdbAccess = session.get('decommdb_access')
    except:
        decommdbAccess = False

    ### Check if user is logged in, if not redirect to login page.
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if adminAccess or decommdbAccess:
        accessGranted = True
    else:
        accessGranted = False

    if not accessGranted:
        error = "you have not been permitted to access that. Please engage with the admins if require this access."
        session['flash_errors'] = error
        return redirect(url_for('main_options'))

    user = session.get('logged_in_user')
    if domain not in user:
        user = user + userDomain

    # message to be displayed to user on live messages page
    liveMessage = "user: '{}' is on the 'Query Decommission DB' Page.".format(user)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('decomm_search_db_options'))
        elif request.form['submit_button'] == 'Search!':
            search_option = request.form['decomm_search_by']
            decommSearchField = request.form['decomm_search_field']
            searchColumn = str()
            fieldToSearch = str()

            if search_option == "Hostname":
                searchColumn = "host_name"
                decommHostnames = decommSearchField
                decommHostnamesList = decommHostnames.split()
                if len(decommHostnamesList) > 0:
                    for server in decommHostnamesList:
                        fieldToSearch = fieldToSearch  + '\'' + server  + '\'' + ','
                    fieldToSearch = fieldToSearch[:-1]

                # messages to be displayed to user on live messages page
                liveMessage = "user: '{}' opted to query: '{}' on DB Table: '{}' on DB: '{}'.".format(user, search_option, dbTableName, dbName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                liveMessage = "'{}/s' queried by user: '{}':".format(search_option, user)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                for server in decommHostnamesList:
                    liveMessage = "'{}'".format(server)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

            elif search_option == "Change Order":
                searchColumn = "change_number"
                fieldToSearch = '\'' + decommSearchField.upper() + '\''

                # message to be displayed to user on live messages page
                liveMessage = "user: '{}' opted to query: '{}' on DB Table: '{}' on DB: '{}'.".format(user, search_option, dbTableName, dbName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                liveMessage = "'{}' queried by user: '{}': {}".format(search_option, user, fieldToSearch)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

            elif search_option == "Actioned By":
                searchColumn = "actioned_by"
                fieldToSearch = '\'' + decommSearchField.lower() + '\''
                # message to be displayed to user on live messages page
                liveMessage = "user: '{}' opted to query: '{}' on DB Table: '{}' on DB: '{}'.".format(user, search_option, dbTableName, dbName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                liveMessage = "Decomms '{}': {} queried by user: '{}'.".format(search_option, fieldToSearch, user)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

            elif search_option == "Date":

                # message to be displayed to user on live messages page
                liveMessage = "user: '{}' opted to query: '{}' on DB Table: '{}' on DB: '{}'.".format(user, search_option, dbTableName, dbName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)


                decommSearchFromDate = request.form['decomm_from_date']
                decommSearchFromDate = decommSearchFromDate.replace(". ","-")
                decommSearchFromDateList = decommSearchFromDate.split('-')
                fromDay = int(decommSearchFromDateList[0])
                fromMonth = int(decommSearchFromDateList[1])
                fromYear = int(decommSearchFromDateList[2])
                if len(str(fromDay)) == 1:
                    fromDay = '0' + str(fromDay)
                    fromDay = int(fromDay)

                decommSearchToDate = request.form['decomm_to_date']
                decommSearchToDate = decommSearchToDate.replace(". ","-")
                decommSearchToDateList = decommSearchToDate.split('-')
                toDay = int(decommSearchToDateList[0])
                toMonth = int(decommSearchToDateList[1])
                toYear = int(decommSearchToDateList[2])
                if len(str(toDay)) == 1:
                    toDay = '0' + str(toDay)
                    toDay = int(toDay)

                searchColumn = "date_time_actioned"

                fromDate = datetime(fromYear, fromMonth, fromDay)
                toDate = datetime(toYear, toMonth, toDay)

                # message to be displayed to user on live messages page
                liveMessage = "'{}s' queried by user: '{}':".format(search_option, user)
                print(liveMessage)
                general.showUserMessage(liveMessage)

                liveMessage = "FROM: '{}' TO: '{}'".format(fromDate, toDate)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                if fromDate > toDate:
                    error = "FROM date CANNOT be GREATER than TO date, please try again..."
                    session['flash_errors'] = error
                    print(error)

            if search_option == "Date":
                # add 1 day to 'toDate' so that Select query has a range to work with.
                # this is NEEDED for our implementation of datetime in our database.
                toDate = toDate + timedelta(days=1)
                fromDate = str(fromDate)[:10]
                toDate = str(toDate)[:10]
                selectQuery = "SELECT * FROM {} WHERE {} >= '{}' AND {} <= '{}';".format(
                                dbTableName,
                                searchColumn,
                                fromDate,
                                searchColumn,
                                toDate
                )
            else:
                selectQuery = "SELECT * FROM {} WHERE {} IN ({});".format(
                                dbTableName,
                                searchColumn,
                                fieldToSearch
                )

            try:
                selectResults = common_functions.dbQueryExecutor(dbName, selectQuery)
                print("*" * 50)
                print()
            except Exception as e:
                print("error:")
                print(e)
            print()

            session['decomm_db_select_results'] = selectResults

            for key, values in selectResults.items():
                img_url = str()
                valuesList = list()
                for value in values:
                    if value == "N":
                        value = Markup(startImgTag + quoteStr + null_img_url + quoteStr + endImgTag)
                    elif value == "Y":
                        value = Markup(startImgTag + quoteStr + tick_img_url + quoteStr + tickEndImgTag)
                    elif value == "F":
                        value = Markup(startImgTag + quoteStr + cross_img_url + quoteStr + tickEndImgTag)
                    valuesList.append(value)
                updatedSelectResults[key] = valuesList

            session['display_select_results_decomm_db'] = updatedSelectResults

            totalRecords = len(updatedSelectResults)
            session['display_total_records_decomm_db'] = totalRecords

            try:
                error = session.get('flash_errors')
            except:
                error = None

            if error is None:
                return redirect(url_for('display_search_info_decomm_db'))
            elif error != None:
                flash(error)
                error = None
                session['flash_errors'] = error

        else:
            pass

    return render_template('decomm/get_search_db_info.html')


@bp.route('/decomm/set_graph_results', methods=('GET', 'POST'))
def set_graph_results_decomm_db():
    searchFor = None
    selectResults = dict()
    updatedSelectResults = dict()
    try:
        fromDate = session.get('search_decomm_db_from_date')
    except Exception as e:
        fromDate = None
        print("Exception caught: '{}'".format(str(e)))

    try:
        toDate = session.get('search_decomm_db_to_date')
    except Exception as e:
        toDate = None
        print("Exception caught: '{}'".format(str(e)))

    try:
        jsonSearchForData = request.get_json().get('search_for')
    except Exception as e:
        print("Exception caught: '{}'".format(str(e)))
        jsonSearchForData = None

    if jsonSearchForData != None and jsonSearchForData != "Total":
        searchFor = re.search(r'\((.*?)\)', jsonSearchForData).group(1)
    elif jsonSearchForData != None and jsonSearchForData == "Total":
        searchFor = jsonSearchForData
    else:
        searchFor = None

    if searchFor != None:
        session['searchFor_this'] = searchFor

    try:
        jsonGraphTitleData = request.get_json().get('graph_title')
    except Exception as e:
        print("Exception caught: '{}'".format(str(e)))
        jsonGraphTitleData = None

    if 'Date' in jsonGraphTitleData:
        if searchFor == 'Total':
            headingValue = "Total Decommissions In Date Range: FROM: '{}' TO: '{}'".format(
                            fromDate,
                            toDate
                            )
            selectQuery = "SELECT * FROM {} WHERE {} >= '{}' AND {} <= '{}';".format(
                            dbTableName,
                            "date_time_actioned",
                            fromDate,
                            "date_time_actioned",
                            toDate
                            )
        else:
            headingValue = "Decommissions Actioned By: '{}', In Date Range: FROM: '{}' TO: '{}'".format(
                            searchFor,
                            fromDate,
                            toDate
                            )
            selectQuery = "SELECT * FROM {} WHERE {} >= '{}' AND {} <= '{}' AND {} = '{}';".format(
                            dbTableName,
                            "date_time_actioned",
                            fromDate,
                            "date_time_actioned",
                            toDate,
                            "actioned_by",
                            searchFor
                            )
    else:
        headingValue = "Decommissions Actioned By: '{}'".format(searchFor)
        selectQuery = "SELECT * FROM {} WHERE {} = '{}';".format(
        dbTableName,
        "actioned_by",
        searchFor
        )

    session['display_decomm_heading_value'] = headingValue

    try:
        selectResults = common_functions.dbQueryExecutor(dbName, selectQuery)
    except Exception as e:
        print("Exception caught: '{}'".format(str(e)))

    session['decomm_db_select_results'] = selectResults

    for key, values in selectResults.items():
        img_url = str()
        valuesList = list()
        for value in values:
            if value == "N":
                value = Markup(startImgTag + quoteStr + null_img_url + quoteStr + endImgTag)
            elif value == "Y":
                value = Markup(startImgTag + quoteStr + tick_img_url + quoteStr + tickEndImgTag)
            elif value == "F":
                value = Markup(startImgTag + quoteStr + cross_img_url + quoteStr + tickEndImgTag)
            valuesList.append(value)
        updatedSelectResults[key] = valuesList

    session['display_select_results_decomm_db'] = updatedSelectResults

    totalRecords = len(updatedSelectResults)
    session['display_total_records_decomm_db'] = totalRecords

    session['page_to_go_back_to_decomm_db_querying'] = "graphs_search_decomm_stats"

    return jsonify(status="success", data=jsonSearchForData)


@bp.route('/decomm/display_search_info', methods=('GET', 'POST'))
def display_search_info_decomm_db():

    try:
        headingValue = session.get('display_decomm_heading_value')
    except:
        headingValue = None
    try:
        selectResults = session.get('decomm_db_select_results')
    except:
        selectResults = dict()
    try:
        updatedSelectResults = session.get('display_select_results_decomm_db')
    except:
        updatedSelectResults = dict()
    try:
        totalRecords = session.get('display_total_records_decomm_db')
    except:
        totalRecords = 0
    try:
        backToGoBackTo = session.get('page_to_go_back_to_decomm_db_querying')
    except:
        backToGoBackTo = "main_options"
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
        decommdbAccess = session.get('decommdb_access')
    except:
        decommdbAccess = False

    ### Check if user is logged in, if not redirect to login page.
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if adminAccess or decommdbAccess:
        accessGranted = True
    else:
        accessGranted = False

    if not accessGranted:
        error = "you have not been permitted to access that. Please engage with the admins if require this access."
        session['flash_errors'] = error
        return redirect(url_for('main_options'))

    user = session.get('logged_in_user')
    if domain not in user:
        user = user + userDomain

    # message to be displayed to user on live messages page
    liveMessage = "user: '{}' is on the 'Display Query Decomm DB Results' Page.".format(user)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)


    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back' and backToGoBackTo == decommDBMenuPage:
            return redirect(url_for(decommDBMenuPage))
        elif request.form['submit_button'] == 'Back' and backToGoBackTo == getSearchInfoPage:
            return redirect(url_for(getSearchInfoPage))
        elif request.form['submit_button'] == 'Back' and backToGoBackTo == "graphs_search_decomm_stats":
            return "<script>window.onload = window.close();</script>"
        elif request.form['submit_button'] == 'Back' and backToGoBackTo == "":
            return redirect(url_for(decommDBMenuPage))
        elif request.form['submit_button'] == 'Download':
            decomm_download_file = download_decomm_db_options.download_selected(selectResults)
            return send_file(decomm_download_file, as_attachment=True)

    return render_template('decomm/display_decomm_db_results.html',
                            heading_value = headingValue,
                            selectResultsDict = updatedSelectResults,
                            total_records = totalRecords)
