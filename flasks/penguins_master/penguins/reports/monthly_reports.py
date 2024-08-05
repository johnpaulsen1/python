import functools, io, ast
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from penguins.auth import logout, domain, userDomain

from penguins.other_utils import general

bp = Blueprint('monthly_reports', __name__, url_prefix='/penguins')

# options
@bp.route('/report_options', methods=('GET', 'POST'))
def report_main():

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

    user = session.get('logged_in_user')
    if domain not in user:
        user = user + userDomain

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('main_options'))
        elif request.form['submit_button'] == "Availability":
            return redirect(url_for('gen_available'))
        elif request.form['submit_button'] == "View Current":
            return redirect(url_for('view_current'))
        elif request.form['submit_button'] == 'View Historic':
            return redirect(url_for('historic'))
        else:
            pass

    return render_template('reports/main.html')
