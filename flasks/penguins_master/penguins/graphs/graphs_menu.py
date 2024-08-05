from flask import (
    Blueprint, redirect, render_template, request, session, url_for, flash
)
from penguins.auth import logout, domain, userDomain

# initialize variables
bp = Blueprint('graphs_menu', __name__, url_prefix='/penguins')

default_graph_type = "Bar Graph"
# default_graph_type = "Pie Chart"
# default_graph_type = "Line Graph"

# options
@bp.route('/graphs', methods=('GET', 'POST'))
def graphs_options():
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
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('main_options'))

        elif request.form['submit_button'] == 'Config Managers':
            selectedGraph = "graphs_config_managers"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = selectButton
            backToPage = "graphs_options"
            session['back_to_page'] = backToPage
            if default_graph_type == 'Bar Graph':
                session['graph_type_title'] = selectButton
                return redirect(url_for('bar'))
            elif default_graph_type == 'Pie Chart':
                session['graph_type_title'] = selectButton
                return redirect(url_for('pie'))

        elif request.form['submit_button'] == 'OS Version Stats':
            selectedGraph = "graphs_os_version_stats"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = selectButton
            backToPage = "graphs_options"
            session['back_to_page'] = backToPage
            if default_graph_type == 'Bar Graph':
                session['graph_type_title'] = selectButton
                return redirect(url_for('multi_bars'))
            elif default_graph_type == 'Pie Chart':
                session['graph_type_title'] = selectButton
                return redirect(url_for('multi_pies'))

        elif request.form['submit_button'] == 'Agent Versions Installed':
            selectedGraph = "graphs_agent_versions_installed"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = selectButton
            backToPage = "graphs_options"
            session['back_to_page'] = backToPage
            if default_graph_type == 'Bar Graph':
                session['graph_type_title'] = selectButton
                return redirect(url_for('multi_bars'))
            elif default_graph_type == 'Pie Chart':
                session['graph_type_title'] = selectButton
                return redirect(url_for('multi_pies'))

        elif request.form['submit_button'] == 'Agents Health Check':
            selectedGraph = "graphs_agents_health_check"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = selectButton
            backToPage = selectedGraph
            session['back_to_page'] = backToPage
            return redirect(url_for(selectedGraph))

        elif request.form['submit_button'] == 'BU Footprint Stats':
            selectedGraph = "graphs_bu_footprint_stats"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = selectButton
            backToPage = "graphs_options"
            session['back_to_page'] = backToPage
            if default_graph_type == 'Bar Graph':
                session['graph_type_title'] = selectButton
                return redirect(url_for('bar'))
            elif default_graph_type == 'Pie Chart':
                session['graph_type_title'] = selectButton
                return redirect(url_for('pie'))

        elif request.form['submit_button'] == 'Environment Footprint Stats':
            selectedGraph = "graphs_env_footprint_stats"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = selectButton
            backToPage = "graphs_options"
            session['back_to_page'] = backToPage
            if default_graph_type == 'Bar Graph':
                session['graph_type_title'] = selectButton
                return redirect(url_for('bar'))
            elif default_graph_type == 'Pie Chart':
                session['graph_type_title'] = selectButton
                return redirect(url_for('pie'))

        elif request.form['submit_button'] == 'Server Type Stats':
            selectedGraph = "graphs_server_type_stats"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = selectButton
            backToPage = "graphs_options"
            session['back_to_page'] = backToPage
            if default_graph_type == 'Bar Graph':
                session['graph_type_title'] = selectButton
                return redirect(url_for('bar'))
            elif default_graph_type == 'Pie Chart':
                session['graph_type_title'] = selectButton
                return redirect(url_for('pie'))

        elif request.form['submit_button'] == 'Greatwall Stats':
            selectedGraph = "graphs_greatwall_stats"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = selectButton
            backToPage = "graphs_options"
            session['back_to_page'] = backToPage
            if default_graph_type == 'Bar Graph':
                session['graph_type_title'] = selectButton
                return redirect(url_for('bar'))
            elif default_graph_type == 'Pie Chart':
                session['graph_type_title'] = selectButton
                return redirect(url_for('pie'))

        elif request.form['submit_button'] == 'AD Auth Stats':
            selectedGraph = "graphs_ad_auth_stats"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = selectButton
            backToPage = "graphs_options"
            session['back_to_page'] = backToPage
            if default_graph_type == 'Bar Graph':
                session['graph_type_title'] = selectButton
                return redirect(url_for('bar'))
            elif default_graph_type == 'Pie Chart':
                session['graph_type_title'] = selectButton
                return redirect(url_for('pie'))

        elif request.form['submit_button'] == 'Decomm Stats':
            selectedGraph = "graphs_search_decomm_stats"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = selectButton
            backToPage = selectedGraph
            session['back_to_page'] = backToPage
            return redirect(url_for(selectedGraph))

        else:
            pass

    return render_template('graphs/options.html')


@bp.route('/graphs/agents_health_check', methods=('GET', 'POST'))
def graphs_agents_health_check():
    try:
        graphTitle = session.get('graph_title')
    except:
        graphTitle = "Graph Options"

    try:
        selectedGraph = session.get('selected_graph')
    except:
        selectedGraph = "graphs_options"

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
        singularGraphTitle = "Agent Health Check"
        selectButton = request.form['submit_button']
        if selectButton == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif selectButton == 'Back':
            return redirect(url_for('graphs_options'))

        elif selectButton == 'Splunk':
            graphTitle = selectButton + " - " + singularGraphTitle
            selectedGraph = "graphs_splunk_health_check"
            session['selected_graph'] = selectedGraph
            session['graph_title'] = graphTitle
            if default_graph_type == 'Bar Graph':
                session['graph_type_title'] = graphTitle
                return redirect(url_for('bar'))
            elif default_graph_type == 'Pie Chart':
                session['graph_type_title'] = graphTitle
                return redirect(url_for('pie'))
        else:
            pass

    return render_template('graphs/agents_health_check.html', title=graphTitle)


@bp.route('/graphs/search_decomm_stats', methods=('GET', 'POST'))
def graphs_search_decomm_stats():
    try:
        graphTitle = session.get('graph_title')
    except:
        graphTitle = "Graph Options"

    try:
        selectedGraph = session.get('selected_graph')
    except:
        selectedGraph = "graphs_options"

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
            return redirect(url_for('graphs_options'))
        elif selectButton == 'SEARCH':
            search_option = request.form['decomm_search_by']
            decommSearchField = request.form['decomm_search_field']
            graph_type_selected = request.form['graph_type']
            searchColumn = str()
            fieldToSearch = str()

            if search_option == "All":
                legendTitle = "All Decomm Stats"
                session['display_legend'] = legendTitle

            elif search_option == "Change Order":
                searchColumn = "change_number"
                fieldToSearch = '\'' + decommSearchField.upper() + '\''
                session['decomm_db_query_search_column'] = searchColumn
                session['decomm_db_query_search_field'] = fieldToSearch

                legendTitle = "Decomm Stats for Change Order: {}".format(
                            decommSearchField.upper()
                            )
                session['display_legend'] = legendTitle

            elif search_option == "Actioned By":
                searchColumn = "actioned_by"
                fieldToSearch = '\'' + decommSearchField.lower() + '\''
                session['decomm_db_query_search_column'] = searchColumn
                session['decomm_db_query_search_field'] = fieldToSearch

                legendTitle = "Decomm Stats for User: {}".format(
                            decommSearchField.lower()
                            )
                session['display_legend'] = legendTitle

            elif search_option == "Date":
                decommSearchFromDate = request.form['decomm_from_date']
                decommSearchFromDate = decommSearchFromDate.replace(". ","-")

                decommSearchToDate = request.form['decomm_to_date']
                decommSearchToDate = decommSearchToDate.replace(". ","-")

                session['decomm_search_from_date'] = decommSearchFromDate
                session['decomm_search_to_date'] = decommSearchToDate

                legendTitle = "Decomm Stats for date range: FROM: {}, TO: {}".format(
                            decommSearchFromDate,
                            decommSearchToDate
                            )

                session['display_legend'] = legendTitle

                if decommSearchFromDate == '' or decommSearchToDate == '':
                    error = "Please select FROM and TO date range."
                    session['flash_errors'] = error
                    flash(error)

            if graph_type_selected == "Bar Graph":
                graphTitle = "Decomm Stats By: '{}'".format(search_option)
                session['graph_type_title'] = graphTitle
                return redirect(url_for('bar'))
            elif graph_type_selected == "Pie Graph":
                graphTitle = "Decomm Stats By: '{}'".format(search_option)
                session['graph_type_title'] = graphTitle
                return redirect(url_for('pie'))
            elif graph_type_selected == "Line Graph":
                graphTitle = "Decomm Stats By: '{}'".format(search_option)
                session['graph_type_title'] = graphTitle
                return redirect(url_for('line'))

    return render_template('graphs/search_decomm_stats.html', title=graphTitle)
