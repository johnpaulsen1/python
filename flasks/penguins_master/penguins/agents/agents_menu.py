from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
from penguins.auth import logout

bp = Blueprint('agents_menu', __name__, url_prefix='/penguins')

# options
@bp.route('/agents', methods=('GET', 'POST'))
def agents_options():
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
            return redirect(url_for('main_options'))
        elif selectButton == 'Health Check Status':
            selectedPage = "agents_health_check_selection"
            session['selected_page'] = selectedPage
            session['page_title'] = selectButton
            return redirect(url_for('agents_health_check_selection'))
        else:
            pass

    return render_template('agents/options.html')
