from flask import (
    Blueprint, redirect, render_template, request, session, url_for, send_file
)
from datetime import datetime
import os
from penguins.auth import logout, domain, userDomain
from penguins.other_utils import general
from penguins.decomm import download_decomm_db_options

# initialize variables
bp = Blueprint('server_decomm_search_db_menu', __name__, url_prefix='/penguins')
user = str()

@bp.route('/decomm/search_db_menu', methods=('GET', 'POST'))
def decomm_search_db_options():

    session['display_decomm_heading_value'] = str()
    session['display_select_results_decomm_db'] = str()
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
    liveMessage = "user: '{}' is in the 'Search Decommission DB Menu'.".format(user)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('decomm_options'))
        elif request.form['submit_button'] == 'Show ALL Actioned Decomms':
            return redirect(url_for('decomm_show_all_decomm_db'))
        elif request.form['submit_button'] == 'Search Actioned Decomms':
            return redirect(url_for('input_search_info_decomm_db'))
        elif request.form['submit_button'] == 'Download Decomm Report':
            decomm_download_file = download_decomm_db_options.download_all()
            return send_file(decomm_download_file, as_attachment=True)
        else:
            pass

    return render_template('decomm/search_decomm_db_options.html')
