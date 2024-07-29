from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
from penguins.auth import logout, domain, userDomain
from penguins.other_utils import general

# initialize variables
bp = Blueprint('server_decomm_menu', __name__, url_prefix='/penguins')
user = str()

@bp.route('/decomm', methods=('GET', 'POST'))
def decomm_options():
    # checks if user is logged in, if not, user will be redirected to login page

    session['servers_found_in_puppet_list'] = list()
    session['servers_not_found_in_puppet_list'] = list()

    session['servers_in_vsphere_list'] = list()
    session['servers_not_in_vsphere_list'] = list()
    session['vcs_vms_in_vspheredb_dict'] = list()

    session['list_of_servers_able_to_ssh'] = list()
    session['list_of_servers_unable_to_ssh'] = list()

    session['servers_in_satellite_list'] = list()
    session['servers_not_in_satellite_list'] = list()

    session['server_names_list'] = list()

    session['change_order_number'] = str()

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
    liveMessage = "user: '{}' is in the 'Decommission Menu'.".format(user)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    if adminAccess:
        adminVisibility = "visibility_on"
        decommdbVisibility = "visibility_on"
    else:
        adminVisibility = "visibility_off"

    if decommdbAccess or adminAccess:
        decommdbVisibility = "visibility_on"
    else:
        decommdbVisibility = "visibility_off"


    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('main_options'))
        elif request.form['submit_button'] == 'Decomm Server/s':
            return redirect(url_for('decomm_server_get_info'))
        elif request.form['submit_button'] == 'Query Decomm DB':
            return redirect(url_for('decomm_search_db_options'))
        else:
            pass

    return render_template('decomm/options.html',
                            setAdminVisibility = adminVisibility,
                            setDecommdbVisibility = decommdbVisibility)
