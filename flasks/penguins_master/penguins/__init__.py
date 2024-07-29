from flask import Flask, session
from flask_session import Session
from datetime import timedelta
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
from pubsub import pub
import logging
from penguins import (auth, other, main_options, cmdb, satellite, links, tmc, patch)
from penguins.reports import (monthly_reports, generate_availability)
from penguins.vsphere import (vsphere_menu, vsphere_search, vsphere_found)
from penguins.ansible import ansible_main
from penguins.decomm import (server_decomm_menu, server_decomm_actions, server_decomm_report, server_decomm_search_db_menu, query_decomm_db)
from penguins.other_utils import general
from penguins.graphs import (graphs_menu, graphs_display)
from penguins.agents import (agents_menu, health_check_status)

app = Flask(__name__)
app.config["SECRET_KEY"] = b'not ever.....'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Define Flask-login configuration
login_mgr = LoginManager(app)
login_mgr.login_view = 'login'
login_mgr.refresh_view = 'relogin'
login_mgr.needs_refresh_message = (u"Session timedout, please login again")
login_mgr.needs_refresh_message_category = "info"

logFileName = '/opt/flask/logs/flasky.log'

@app.before_request
def before_request():
    app.permanent_session_lifetime = timedelta(minutes=60)

def create_app():
    # create and configure the app

    # set up logging for the app
    logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s', filename=logFileName, level=logging.DEBUG)
    logging.info("Flasky app started and running...")

    # configure web app routing
    app.register_blueprint(auth.bp)
    app.add_url_rule('/', endpoint='home')
    app.add_url_rule('/penguins', endpoint='home')
    app.add_url_rule('/penguins/login', endpoint='login')
    app.add_url_rule('/penguins/ldap', endpoint='ldap_main')
    app.add_url_rule('/penguins/ldap/user_details', endpoint='ldap_user_details')
    app.add_url_rule('/penguins/ldap/users_group_membership', endpoint='ldap_users_group_membership')
    app.add_url_rule('/penguins/ldap/group_members', endpoint='ldap_group_members')
    app.add_url_rule('/penguins/ldap/unix_groups', endpoint='ldap_unix_groups')
    app.add_url_rule('/penguins/ldap/check_user_lock_status', endpoint='ldap_user_lock_status')

    app.register_blueprint(main_options.bp)
    app.add_url_rule('/penguins/main', endpoint='main_options')

    app.register_blueprint(other.bp)
    app.add_url_rule('/penguins/burger', endpoint='burger')
    app.add_url_rule('/penguins/coming_soon', endpoint='coming_soon')
    app.add_url_rule('/penguins/live_server_messages', endpoint='live_server_messages')

    app.register_blueprint(cmdb.bp)
    app.add_url_rule('/penguins/cmdb', endpoint='cmdb')
    app.add_url_rule('/penguins/cmdb/current', endpoint='cmdb_current')
    app.add_url_rule('/penguins/cmdb/search', endpoint='input_search_info_cmdb')
    app.add_url_rule('/penguins/cmdb/display_search_info',endpoint='display_search_info_cmdb')
    app.add_url_rule('/penguins/cmdb/download', endpoint='download_cmdb')

    app.register_blueprint(tmc.bp)
    app.add_url_rule('/penguins/tmc', endpoint='tmc_main')
    app.add_url_rule('/penguins/tmc/current', endpoint='tmc_current')
    app.add_url_rule('/penguins/tmc/search', endpoint='input_search_info_tmc')
    app.add_url_rule('/penguins/tmc/display_search_info',endpoint='display_search_info_tmc')
    app.add_url_rule('/penguins/tmc/download', endpoint='download_tmc')
    app.add_url_rule('/penguins/tmc/select_agents_health_check', endpoint='tmc_select_agents_health_check')
    app.add_url_rule('/penguins/tmc/agent_health_check_results', endpoint='tmc_agent_health_check_results')

    app.register_blueprint(patch.bp)
    app.add_url_rule('/penguins/patch_page', endpoint='patch')
    app.add_url_rule('/penguins/patch_page/current_status', endpoint='current_status')
    app.add_url_rule('/penguins/patch_page/patch_stats', endpoint='patch_stats')
    app.add_url_rule('/penguins/patch_page/search', endpoint='search_db')
    app.add_url_rule('/penguins/patch_page/search/hostname', endpoint='search_hostname')
    app.add_url_rule('/penguins/patch_page/search/fact_search', endpoint='search_patch_fact')
    app.add_url_rule('/penguins/patch_page/generate_patch_page', endpoint='generate_patch_page')
    app.add_url_rule('/penguins/patch_page/download/', endpoint='ps_download')

    app.register_blueprint(satellite.bp)
    app.add_url_rule('/penguins/satellite', endpoint='satellite')
    app.add_url_rule('/penguins/subscription_query', endpoint='subscriptions')
    app.add_url_rule('/penguins/patch_query', endpoint='patch_checker')

    app.register_blueprint(monthly_reports.bp)
    app.add_url_rule('/penguins/report_options', endpoint="report_main")

    app.register_blueprint(generate_availability.bp)
    app.add_url_rule('/penguins/report_options/latest_availability', endpoint="gen_available")

    app.register_blueprint(links.bp)
    app.add_url_rule('/penguins/useful_links', endpoint='useful_links')

    app.register_blueprint(server_decomm_menu.bp)
    app.add_url_rule('/penguins/decomm', endpoint='decomm_options')

    app.register_blueprint(server_decomm_actions.bp)
    app.add_url_rule('/penguins/decomm/get_decomm_servers_info', endpoint='decomm_server_get_info')
    app.add_url_rule('/penguins/decomm/check_decomm_servers', endpoint='decomm_server_check')

    app.register_blueprint(server_decomm_report.bp)
    app.add_url_rule('/penguins/decomm/server_decomm_report', endpoint='decomm_report')

    app.register_blueprint(server_decomm_search_db_menu.bp)
    app.add_url_rule('/penguins/decomm/search_db_menu', endpoint='decomm_search_db_options')

    app.register_blueprint(query_decomm_db.bp)
    app.add_url_rule('/penguins/decomm/search_all', endpoint='decomm_show_all_decomm_db')
    app.add_url_rule('/penguins/decomm/input_search_info', endpoint='input_search_info_decomm_db')
    app.add_url_rule('/penguins/decomm/display_search_info', endpoint='display_search_info_decomm_db')
    app.add_url_rule('/penguins/decomm/set_graph_results', endpoint='set_graph_results_decomm_db')

    app.register_blueprint(vsphere_menu.bp)
    app.add_url_rule('/penguins/vsphere', endpoint='vsphere_options')

    app.register_blueprint(vsphere_search.bp)
    app.add_url_rule('/penguins/vsphere/search_vms', endpoint='search_vms')

    app.register_blueprint(vsphere_found.bp)
    app.add_url_rule('/penguins/vsphere/found_vms', endpoint='found_vms')

    app.register_blueprint(ansible_main.bp)
    app.add_url_rule('/penguins/ansible', endpoint='ansible_main')
    app.add_url_rule('/penguins/ansible/results', endpoint='ansible_results')

    app.register_blueprint(graphs_menu.bp)
    app.add_url_rule('/penguins/graphs', endpoint='graphs_options')
    app.add_url_rule('/penguins/graphs/agents_health_check', endpoint='graphs_agents_health_check')
    app.add_url_rule('/penguins/graphs/search_decomm_stats', endpoint='graphs_search_decomm_stats')

    app.register_blueprint(graphs_display.bp)
    app.add_url_rule('/penguins/graphs/bar', endpoint='bar')
    app.add_url_rule('/penguins/graphs/multi_bars', endpoint='multi_bars')
    app.add_url_rule('/penguins/graphs/pie', endpoint='pie')
    app.add_url_rule('/penguins/graphs/multi_pies', endpoint='multi_pies')
    app.add_url_rule('/penguins/graphs/line', endpoint='line')

    app.register_blueprint(agents_menu.bp)
    app.add_url_rule('/penguins/agents', endpoint='agents_options')

    app.register_blueprint(health_check_status.bp)
    app.add_url_rule('/penguins/agents/health_check_selection', endpoint='agents_health_check_selection')
    app.add_url_rule('/penguins/agents/health_check_results', endpoint='agents_health_check_results')

    return app

setApp = create_app()

# turn the flask app into a socketio app
socketio = SocketIO(setApp, async_mode=None, logger=True, engineio_logger=True)

def sendMessage(message):
    print('Function messageToUser received:')
    print('message =', message)
    socketio.emit('newmessage',{'message':message})

pub.subscribe(sendMessage, 'rootMessageSender')

@socketio.on('connect')
def connect():
    liveMessage = "connection established to Flasky's socket."
    logging.info(liveMessage)
    print(liveMessage)
    general.showUserMessage(liveMessage)
