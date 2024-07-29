import functools, io, ast
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Markup
)
from werkzeug.exceptions import abort
from penguins.auth import logout, domain, userDomain
from penguins.flaskdb import common_functions
from penguins.other_utils import general

bp = Blueprint('other', __name__, url_prefix='/penguins')
user = str()

@bp.route('/burger', methods=('GET', 'POST'))
def burger():
    try:
        adminAccess = session.get('admin_access')
    except:
        adminAccess = False

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not adminAccess:
        error = "you have not been permitted to access that. Please engage with the admins if require this access."
        session['flash_errors'] = error
        return redirect(url_for('main_options'))

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('main_options'))
        else:
            pass

    return render_template('other/burger.html')

# options
@bp.route('/coming_soon', methods=('GET', 'POST'))
def comming_soon():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('main_options'))
        else:
            pass

    return render_template('other/coming_soon.html')


dbName = "stack"
dbTableName = "overflow"
columnsList = ["date_time_added",
                    "ref_number",
                    "purchased",
                    "valuated",
                    "cleaned",
                    "actioned_by"]

@bp.route('/live_server_messages', methods=('GET', 'POST'))
def live_server_messages():
    try:
        adminAccess = session.get('admin_access')
    except:
        adminAccess = False

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not adminAccess:
        error = "you have not been permitted to access that. Please engage with the admins if require this access."
        session['flash_errors'] = error
        return redirect(url_for('main_options'))

    user = session.get('logged_in_user')
    if domain not in user:
        user = user + userDomain

    liveMessage = "user: '{}' is on the 'Live Flasky Messages' page.".format(user)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('main_options'))
        else:
            pass

    return render_template('other/live_server_messages.html')
