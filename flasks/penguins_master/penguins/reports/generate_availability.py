import functools, io, ast, os
from flask import (
	Blueprint, Flask, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from penguins.auth import logout, domain, userDomain

from penguins.other_utils import general


bp = Blueprint('generate_availability', __name__, url_prefix='/penguins')


upload_directory = 'penguins/reports/uploads/'
allowed_extensions = ['txt', 'csv']
file_list = list()

# options
@bp.route('/report_options/latest_availability', methods=('GET', 'POST'))
def gen_available():

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
		if request.form['submit_button'] == 'Upload files':
			print(request.files.getlist('file'))
			for file in request.files.getlist('file'):
				if file.filename != '':
					print(file.filename)
					try:
						if file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
							print(file.filename.rsplit('.', 1)[1].lower())
							filename = secure_filename(file.filename)
							dest = os.path.join(upload_directory, filename)
							file.save(dest)
							file_list.append(dest)
							## do some checks and return a generate report button.
							## should be redirect url to the generate report page.
							return render_template('other/coming_soon.html')
						else:
							print("extention not allowed: {}.".format(file.filename.rsplit('.', 1)[1].lower()))
							flash("extention not allowed: {}.".format(file.filename.rsplit('.', 1)[1].lower()))
					except:
						raise

				else:
					print("No file uploaded.")
					flash("No file uploaded - please select and upload at least 2 files.")
					return render_template('reports/generate_new.html')

		elif request.form['submit_button'] == 'Log Out':
			logout()
			return redirect(url_for('login'))
		elif request.form['submit_button'] == 'Back':
			return redirect(url_for('main_options'))
		else:
			pass

	return render_template('reports/generate_new.html')
