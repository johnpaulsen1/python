from flask import (
    Blueprint, redirect, render_template, request, session, url_for
)
from penguins.auth import logout

bp = Blueprint('vsphere_menu', __name__, url_prefix='/penguins')

# options
@bp.route('/vsphere', methods=('GET', 'POST'))
def vsphere_options():
    try:
        adminAccess = session.get('admin_access')
    except:
        adminAccess = False

    ### Check if user is logged in, if not redirect to login page.
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
        elif request.form['submit_button'] == 'Search VMs':
            return redirect(url_for('search_vms'))
        elif request.form['submit_button'] == 'VM Power Actions':
            return redirect(url_for('coming_soon'))
        else:
            pass

    return render_template('vsphere/options.html')
