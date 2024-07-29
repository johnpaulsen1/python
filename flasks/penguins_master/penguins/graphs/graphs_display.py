import math
from flask import (
    Blueprint, redirect, render_template, request, session, url_for, Markup
)
from penguins.auth import logout, domain, userDomain
from penguins.other_utils import general
from penguins.flaskdb import common_functions
from penguins.graphs import (
    config_managers, os_stats, agent_stats, bu_footprint,
    env_footprint, greatwall_stats, ad_auth_stats, server_type_stats,
    splunk_health_check, decomm_stats
    )

# initialize variables
bp = Blueprint('graphs_display', __name__, url_prefix='/penguins')
user = str()

@bp.route('/graphs/bar', methods=('GET', 'POST'))
def bar():

    try:
        selectedGraph = session.get('selected_graph')
    except:
        selectedGraph = "graphs_options"

    try:
        backToPage = session.get('back_to_page')
    except:
        backToPage = "graphs_options"

    try:
        graphTitle = session.get('graph_type_title')
    except:
        graphTitle = "Bar Graph"

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

    ### logic required to set data for specific selected graphs ###
    if selectedGraph == "graphs_config_managers":
        config_managers.getConfigManagerStats()

        legendDisplay = False
        legend = "Puppet vs. Chef"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_bu_footprint_stats":
        bu_footprint.getBUFootprintStats()

        legendDisplay = False
        legend = "Managed BUs Footprint"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_env_footprint_stats":
        env_footprint.getEnvFootprintStats()

        legendDisplay = False
        legend = "Managed ENVs Footprint"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_server_type_stats":
        server_type_stats.getServerTypeStats()

        legendDisplay = False
        legend = "Managed Server Types"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_greatwall_stats":
        greatwall_stats.getGreatwallStats()

        legendDisplay = False
        legend = "Managed Greatwall Stats"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_ad_auth_stats":
        ad_auth_stats.getADAuthStats()

        legendDisplay = False
        legend = "Managed AD Auth Stats"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_splunk_health_check":
        splunk_health_check.getSplunkHealthCheckData()

        legendDisplay = False
        legend = "Splunk Agent Health Stats"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_search_decomm_stats":

        if "Date" in graphTitle:
            decommSearchFromDate = session.get('decomm_search_from_date')
            decommSearchToDate = session.get('decomm_search_to_date')
            decomm_stats.getDecommStatsByDate(decommSearchFromDate, decommSearchToDate)
        elif "Actioned By" in graphTitle or "Change Order" in graphTitle:
            searchColumn = session.get('decomm_db_query_search_column')
            fieldToSearch = session.get('decomm_db_query_search_field')
            decomm_stats.getDecommStatsByUserOrCO(searchColumn, fieldToSearch)
        elif "All" in graphTitle:
            decomm_stats.getAllDecommStats()

        legendDisplay = False
        legend = session.get('display_legend')
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    #################################################################

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for(backToPage))
        else:
            pass

    return render_template('graphs/bar_graph.html', title=graphTitle,
                            max=maxValue, labels=labels, values=values,
                            legend_display=legendDisplay,
                            legend=legend)

@bp.route('/graphs/multi_bars', methods=('GET', 'POST'))
def multi_bars():
    try:
        selectedGraph = session.get('selected_graph')
    except:
        selectedGraph = "graphs_options"

    try:
        backToPage = session.get('back_to_page')
    except:
        backToPage = "graphs_options"

    try:
        graphTitle = session.get('graph_type_title')
    except:
        graphTitle = "Bar Graph"

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

    ### logic required to set data for specific selected graphs ###
    if selectedGraph == "graphs_os_version_stats":
        os_stats.getOSstats()
        multiGraphsDict = session.get('os_families_dict')
        maxValueDict = session.get('graph_max_value_dict')

    if selectedGraph == "graphs_agent_versions_installed":
        agent_stats.getAgentVersionStats()
        multiGraphsDict = session.get('agent_versions_installed_dict')
        maxValueDict = session.get('graph_max_value_dict')


    #################################################################

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for(backToPage))
        else:
            pass

    return render_template('graphs/multiple_bar_graphs.html', title=graphTitle,
                            multiple_graphs_dict=multiGraphsDict,
                            max_dict=maxValueDict
                            )

@bp.route('/graphs/pie', methods=('GET', 'POST'))
def pie():
    try:
        selectedGraph = session.get('selected_graph')
    except:
        selectedGraph = "graphs_options"

    try:
        backToPage = session.get('back_to_page')
    except:
        backToPage = "graphs_options"

    try:
        graphTitle = session.get('graph_type_title')
    except:
        graphTitle = "Pie Chart"

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

    ### logic required to set data for specific selected graphs ###
    if selectedGraph == "graphs_config_managers":
        config_managers.getConfigManagerStats()

        legendDisplay = False
        legend = "Puppet vs. Chef"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_bu_footprint_stats":
        bu_footprint.getBUFootprintStats()

        legendDisplay = False
        legend = "Managed BUs Footprint"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_env_footprint_stats":
        env_footprint.getEnvFootprintStats()

        legendDisplay = False
        legend = "Managed ENVs Footprint"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_server_type_stats":
        server_type_stats.getServerTypeStats()

        legendDisplay = False
        legend = "Managed Server Types"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_greatwall_stats":
        greatwall_stats.getGreatwallStats()

        legendDisplay = False
        legend = "Managed Greatwall Stats"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_ad_auth_stats":
        ad_auth_stats.getADAuthStats()

        legendDisplay = False
        legend = "Managed AD Auth Stats"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_splunk_health_check":
        splunk_health_check.getSplunkHealthCheckData()

        legendDisplay = False
        legend = "Splunk Agent Health Stats"
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    if selectedGraph == "graphs_search_decomm_stats":

        if "Date" in graphTitle:
            decommSearchFromDate = session.get('decomm_search_from_date')
            decommSearchToDate = session.get('decomm_search_to_date')
            decomm_stats.getDecommStatsByDate(decommSearchFromDate, decommSearchToDate)
        elif "Actioned By" in graphTitle or "Change Order" in graphTitle:
            searchColumn = session.get('decomm_db_query_search_column')
            fieldToSearch = session.get('decomm_db_query_search_field')
            decomm_stats.getDecommStatsByUserOrCO(searchColumn, fieldToSearch)
        elif "All" in graphTitle:
            decomm_stats.getAllDecommStats()

        legendDisplay = False
        legend = session.get('display_legend')
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')

    #################################################################

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for(backToPage))
        else:
            pass

    return render_template('graphs/pie_chart.html', title=graphTitle,
                            labels=labels, values=values, legend=legend
                            )

@bp.route('/graphs/multi_pies', methods=('GET', 'POST'))
def multi_pies():
    try:
        selectedGraph = session.get('selected_graph')
    except:
        selectedGraph = "graphs_options"

    try:
        backToPage = session.get('back_to_page')
    except:
        backToPage = "graphs_options"

    try:
        graphTitle = session.get('graph_type_title')
    except:
        graphTitle = "Pie Chart"

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

    ### logic required to set data for specific selected graphs ###
    if selectedGraph == "graphs_os_version_stats":
        os_stats.getOSstats()
        multiGraphsDict = session.get('os_families_dict')

    if selectedGraph == "graphs_agent_versions_installed":
        agent_stats.getAgentVersionStats()
        multiGraphsDict = session.get('agent_versions_installed_dict')

    #################################################################

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for(backToPage))
        else:
            pass

    return render_template('graphs/multiple_pie_charts.html', title=graphTitle,
                            multiple_graphs_dict=multiGraphsDict
                            )

@bp.route('/graphs/line', methods=('GET', 'POST'))
def line():

    try:
        selectedGraph = session.get('selected_graph')
    except:
        selectedGraph = "graphs_options"

    try:
        backToPage = session.get('back_to_page')
    except:
        backToPage = "graphs_options"

    try:
        graphTitle = session.get('graph_type_title')
    except:
        graphTitle = "Line Graph"

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

    ### logic required to set data for specific selected graphs ###
    if selectedGraph == "graphs_search_decomm_stats":

        if "Date" in graphTitle:
            decommSearchFromDate = session.get('decomm_search_from_date')
            decommSearchToDate = session.get('decomm_search_to_date')
            decomm_stats.getDecommStatsByDate(decommSearchFromDate, decommSearchToDate)
        elif "Actioned By" in graphTitle or "Change Order" in graphTitle:
            searchColumn = session.get('decomm_db_query_search_column')
            fieldToSearch = session.get('decomm_db_query_search_field')
            decomm_stats.getDecommStatsByUserOrCO(searchColumn, fieldToSearch)
        elif "All" in graphTitle:
            decomm_stats.getAllDecommStats()

        legendDisplay = False
        legend = session.get('display_legend')
        labels = session.get('graph_labels')
        values = session.get('graph_values')
        maxValue = session.get('graph_max_value')
        numSteps = len(labels) - 2
    #################################################################

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for(backToPage))
        else:
            pass

    return render_template('graphs/line_graph.html', title=graphTitle,
                            max=maxValue, steps=numSteps,
                            labels=labels, values=values,
                            legend_display=legendDisplay,
                            legend=legend)
