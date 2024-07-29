import functools, io, ast, json, pprint, re, requests, getpass, urllib3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from penguins.auth import logout
from penguins.auth import logout, decryptPwd
from penguins.dbquery import makelist
from cryptography.fernet import Fernet

domain = '<domain>'

def sat_api(hostname,user,password):
    global error
    error = None

    if domain not in hostname:
        hostname = hostname + domain

    host_dict = {}
    host_url = "https://<satellite URL>/api/v2/hosts/" + hostname
    req = requests.get(host_url, auth=(user, password),verify=False)
    host_data = req.json()

    try:
        capsule = host_data['subscription_facet_attributes']['registered_through']
    except:
        capsule = "None"

    try:
        esx_host = host_data['subscription_facet_attributes']['virtual_host']['name']
    except:
        try:
            esx_host = host_data['architecture_name']
        except:
            esx_host = "No Data"

    try:
        subscription_status = host_data['subscription_status_label']
    except:
        subscription_status = "No data available"
    try:
        errata_status = host_data['errata_status_label']
        if "Could not" in errata_status:
            errata_status = "Error"
    except:
        pass

    host_dict['hostname'] = hostname
    host_dict['capsule'] = capsule
    host_dict['subscription_status'] = subscription_status
    host_dict['esx_host'] = esx_host
    return host_dict

### Patch Checker goes here....

bp = Blueprint('satellite', __name__, url_prefix='/penguins')

# options
@bp.route('/satellite', methods=('GET', 'POST'))
def satellite():
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
        elif request.form['submit_button'] == "Subscription details":
            return redirect(url_for('subscriptions'))
        elif request.form['submit_button'] == "Patch Status":
            return redirect(url_for('patch_checker'))
        else:
            pass

    return render_template('satellite/main.html')


@bp.route('/subscription_query', methods=('GET', 'POST'))
def subscriptions():
    global error
    headings_list = ['Hostname', 'Subscription Status', 'Capsule', 'ESX']
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
           return redirect(url_for('satellite'))
       elif request.form['submit_button'] == "Submit":
           _key = session.get('sleutel')
           user = session.get('logged_in_user')
           encPwd = session.get('sessEncPwd')
           password = decryptPwd(encPwd, _key)
           hosts = []
           gethosts = request.form.get('Host List')
           h = makelist(gethosts)
           print(h)
           for i in h:
               mynode = sat_api(i,user,password)
               print(mynode)
               hosts.append(mynode)
               print(hosts)
           if error is None:
               return render_template('satellite/subscription_results.html', h=hosts, ListHeadings=headings_list)
           elif error != None:
               flash(error)
               return render_template('satellite/subscription_results.html', h=hosts, ListHeadings=headings_list)
    return render_template('satellite/subscription_query.html')
    # return render_template('satellite/subscription_status.html')

@bp.route('/patch_query', methods=('GET', 'POST'))
def patch_checker():
    global error
    headings_list = ['Hostname', 'Patch Status', 'Last Patched', 'Patch Date', 'Running Kernel', 'Latest Kernel']
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
           return redirect(url_for('satellite'))
       elif request.form['submit_button'] == "Submit":
           _key = session.get('sleutel')
           user = session.get('logged_in_user')
           encPwd = session.get('sessEncPwd')
           password = decryptPwd(encPwd, _key)
           hosts = []
           gethosts = request.form.get('Host List')  #<< get host list from html
           h = makelist(gethosts)  # << creates new list and strips out unneccessary whitespace.
           ## call relevant function i.e patcher.
           print(h)
           for i in h:
            ######
               mynode = sat_api(i,user,password)
               print(mynode)
               hosts.append(mynode)
               print(hosts)
            #####
           if error is None:
               return render_template('satellite/patch_results.html', h=hosts, ListHeadings=headings_list)
           elif error != None:
               flash(error)
               return render_template('satellite/patch_results.html', h=hosts, ListHeadings=headings_list)
    return render_template('satellite/patch_query.html')
    # return render_template('satellite/patch_status.html')
