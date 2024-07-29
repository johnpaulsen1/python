import functools, io, ast
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from penguins.auth import logout

bp = Blueprint('links', __name__, url_prefix='/penguins')

# options
@bp.route('/useful_links', methods=('GET', 'POST'))
def useful_links():
    # checks if user is logged in, if not, user will be redirected to login page
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

    return render_template('useful_links/links.html')
