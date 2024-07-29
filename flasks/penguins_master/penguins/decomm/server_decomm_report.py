from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for,
    Markup, send_file
)
from penguins.auth import logout, domain, userDomain
from penguins.flaskdb import common_functions
from penguins.other_utils import general
from penguins.decomm import download_decomm_db_options

bp = Blueprint('server_decomm_report', __name__, url_prefix='/penguins')

dbName = "decommission"
dbTableName = "decommed_hosts"
selectColumnsList = ["date_time_actioned",
                    "change_number",
                    "host_name",
                    "puppet_decommed",
                    "vsphere_decommed",
                    "satellite_decommed",
                    "physical_decommed",
                    "actioned_by"]
cross_img_url = "/static/images/red-cross.png"
tick_img_url = "/static/images/green-tick.png"
null_img_url = "/static/images/grey-null.png"
quoteStr = "\""
startImgTag = "<img src="
endImgTag = " width=\"30\" height=\"30\"></img>"
tickEndImgTag = " width=\"34\" height=\"34\"></img>"

stars = "*" * 70

@bp.route('/decomm/server_decomm_report', methods=('GET', 'POST'))
def decomm_report():
    headingValue = "Post Decommission Report"
    selectResults = dict()
    updatedSelectResults = dict()
    try:
        userRequestedDecommServers = session.get('server_names_list')
    except:
        changeOrderNumber = str()
    try:
        changeOrderNumber = session.get('change_order_number')
    except:
        userRequestedDecommServers = list()
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
    liveMessage = "user: '{}' is on the 'Decommission Server Report' Page.".format(user)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    # print()
    # print(userRequestedDecommServers)
    serversToSearch = str()
    for server in userRequestedDecommServers:
        print(server)
        serversToSearch = serversToSearch  + '\'' + server  + '\'' + ','

    if userRequestedDecommServers != None:
        selectQuery = "SELECT * FROM {} WHERE {} IN ({}) AND {} = {};".format(
                        # selectColumnsStr[:-1],
                        dbTableName,
                        "host_name",
                        serversToSearch[:-1],
                        "change_number",
                        str('\''+changeOrderNumber+'\'')
        )

        try:
            selectResults = common_functions.dbQueryExecutor(dbName, selectQuery)

            # message to be displayed to user on live messages page
            liveMessage = stars
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            liveMessage = selectResults
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

        except Exception as e:
            # message to be displayed to user on live messages page
            error = "an error occured while retrieving 'SELECT' results from Table: '{}' on DB: '{}'".format(dbTableName, dbName)
            print(error)
            print()
            general.showUserMessage(error)

            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))

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

        totalRecords = len(updatedSelectResults)


    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('decomm_server_get_info'))
        elif request.form['submit_button'] == 'Download':
            decomm_download_file = download_decomm_db_options.download_selected(selectResults)
            return send_file(decomm_download_file, as_attachment=True)
        else:
            pass

    return render_template('decomm/display_decomm_db_results.html',
                            heading_value = headingValue,
                            selectResultsDict = updatedSelectResults,
                            total_records = totalRecords)
