import functools, io, ast
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from penguins.auth import logout

bp = Blueprint('main_options', __name__, url_prefix='/penguins')

# options
@bp.route('/main', methods=('GET', 'POST'))
def main_options():
    try:
        adminAccess = session.get('admin_access')
        cmdbAccess = session.get('cmdb_access')
        decommdbAccess = session.get('decommdb_access')
    except:
        adminAccess = False
        cmdbAccess = False
        decommdbAccess = False

    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    if adminAccess:
        adminVisibility = "visibility_on"
        cmdbVisibility = "visibility_on"
        decommdbVisibility = "visibility_on"
    else:
        adminVisibility = "visibility_off"

    if cmdbAccess or adminAccess:
        cmdbVisibility = "visibility_on"
    else:
        cmdbVisibility = "visibility_off"

    if decommdbAccess or adminAccess:
        decommdbVisibility = "visibility_on"
    else:
        decommdbVisibility = "visibility_off"

    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if session.get('already_logged_in'):
        error = session['already_logged_in']

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'LDAP':
            return redirect(url_for('ldap_main'))
        elif request.form['submit_button'] == 'CMDB':
            return redirect(url_for('cmdb'))
        elif request.form['submit_button'] == 'TMC':
            return redirect(url_for('tmc_main'))
        elif request.form['submit_button'] == 'Agents Health Status':
            return redirect(url_for('agents_health_check_selection'))
        elif request.form['submit_button'] == 'Reports':
            return redirect(url_for('report_main'))
        elif request.form['submit_button'] == 'Graphs':
            return redirect(url_for('graphs_options'))
        elif request.form['submit_button'] == 'Patch Page':
            return redirect(url_for('patch'))
        elif request.form['submit_button'] == 'Decomm Servers':
            return redirect(url_for('decomm_options'))
        elif request.form['submit_button'] == 'Vsphere':
            return redirect(url_for('vsphere_options'))
        elif request.form['submit_button'] == 'Live Flasky Messages':
            return redirect(url_for('live_server_messages'))
        elif request.form['submit_button'] == 'Ansible':
            return redirect(url_for('ansible_main'))
        elif request.form['submit_button'] == 'Useful Links':
            return redirect(url_for('useful_links'))
        elif request.form['submit_button'] == 'Burger':
            return redirect(url_for('burger'))
        else:
            pass

    if error is None:
        return render_template('logged_in/main_options.html',
                                setAdminVisibility = adminVisibility,
                                setCMDBVisibility = cmdbVisibility,
                                setDecommdbVisibility = decommdbVisibility)
    elif error != None:
        flash(error)
        error = None
        session['flash_errors'] = error
        session['already_logged_in'] = None

    return render_template('logged_in/main_options.html',
                            setAdminVisibility = adminVisibility,
                            setCMDBVisibility = cmdbVisibility,
                            setDecommdbVisibility = decommdbVisibility)
