from pypuppetdb import connect
import functools, io, ast, os, sys, re, pprint, json, requests, time
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from penguins.auth import logout

### Functions
source_list = (os.getcwd() + "/penguins/static/source_list")
domain = "<domain>"

def clean():
    try:
        if os.path.isfile(source_list):
            os.remove(source_list)
    except IOError:
        pass

def generate_list():
    #listA = []
    #host_list = []
    db = connect(host='x.x.x.x')
    nodes = db.nodes()

    bu = 'fnb_bu'
    role = 'fnb_server_role'
    virt = 'virtual'
    osversion = 'lsbdistrelease'
    host_list = []
    count = 0
    for node in nodes:
        # Fact: BU
        host_bu = 'http://x.x.x.x:8080/v3/nodes/' + str(node) + '/facts/' + str(bu)
        req = requests.get(host_bu)
        host_data = req.json()
        try:
          x = host_data[0]
        except IndexError:
          pass
        #print(x['value'] + '/' + str(node))
        # Fact: FNB_SERVER_ROLE
        host_server_role = 'http://x.x.x.x:8080/v3/nodes/' + str(node) + '/facts/' + str(role)
        req = requests.get(host_server_role)
        host_data1= req.json()
        try:
          y = host_data1[0]
        except IndexError:
          pass
        #print(x['value'] + '/' + y['value'] + '/' + str(node))
        #print(x['value'] + '/' + str(node))
        # FACT: VIRTUAL/PHYSICAL/ZLINUX
        host_arch = 'http://x.x.x.x:8080/v3/nodes/' + str(node) + '/facts/' + str(virt)
        req = requests.get(host_arch)
        host_data2= req.json()
        try:
          z = host_data2[0]
        except IndexError:
          pass
        host_osversion = 'http://x.x.x.x:8080/v3/nodes/' + str(node) + '/facts/' + str(osversion)
        req = requests.get(host_osversion)
        host_data2= req.json()
        try:
          a = host_data2[0]
        except IndexError:
          pass
        #print(x['value'] + '/' + y['value'] + '/' + z['value'] +  '/' + str(node))
        host_entry = x['value'] + ':' + y['value'] + ':' + z['value'] + ':' + a['value'] + ':' + str(node)
        #print(host_entry)
        host_list.append(host_entry)

    with open(source_list,"w+") as f:
        for i in host_list:
            f.write(i + '\n')


def fetch_node(hostname):
    global error
    error = None
    #listA = []
    #host_list = []

    if domain not in hostname:
        hostname = hostname + domain

    print(hostname)
    db = connect(host='x.x.x.x')
    nodes = db.nodes()
    bu = 'fnb_bu'
    role = 'fnb_server_role'
    virt = 'virtual'
    osversion = 'lsbdistrelease'
    distro = 'operatingsystem'
    cost_centre = 'fnb_cost_centre'
    company_code = 'fnb_company_code'
    host_dict = {}
    host_dict['hostname'] = str(hostname)
    interesting_fact = ''
    fact_list = ['fnb_bu','fnb_server_role','virtual','lsbdistrelease','operatingsystem','fnb_company_code','fnb_cost_centre' ]

    for fact in fact_list:
        try:
            host_bu = 'http://x.x.x.x:8080/v3/nodes/' + str(hostname) + '/facts/' + fact
            req = requests.get(host_bu)
            host_data = req.json()
            interesting_fact = host_data[0]
            host_dict[fact] = str(interesting_fact['value'])
        except:
          error = "Host not found"
    print(host_dict)
    return host_dict

def getAge():
    mod_age = os.path.getmtime(source_list)
    cur_time = time.time()
    diff = (((cur_time - mod_age)/60)/60)/24
    print(diff)
    if diff < 7:
        return 0
    else:
        return 1

def parseHosts():
    server_list = []
    r5count = 0
    r6count = 0
    r7count = 0
    unknown = 0
    with open(source_list,"r") as f:
        for line in f.readlines():
            nline = line.split(':')
            server_list.append(nline[4].rstrip('\n'))

#    print('RHEL5: ' + str(r5count))
#    print('RHEL6: ' + str(r6count))
#    print('RHEL7: ' + str(r7count))
#    print('Unknown OS: ' + str(unknown))
    return server_list

def count5():
    r5count = 0
    with open(source_list,"r") as f:
        for line in f.readlines():
            nline = line.split(':')
            osfield = nline[3]
            if re.search('^5.*', osfield):
                r5count += 1
            else:
                pass
    return r5count

def count6():
    r6count = 0
    with open(source_list,"r") as f:
        for line in f.readlines():
            nline = line.split(':')
            osfield = nline[3]
            if re.search('^6.*', osfield):
                r6count += 1
            else:
                pass
    return r6count

def count7():
    r7count = 0
    with open(source_list,"r") as f:
        for line in f.readlines():
            nline = line.split(':')
            osfield = nline[3]
            if re.search('^7.*', osfield):
                r7count += 1
            else:
                pass
    return r7count


def makelist(hlist):
    sl = str(hlist)
    nl = sl.split()
    return nl

### Webpages
bp = Blueprint('dbquery', __name__, url_prefix='/penguins')
# options
@bp.route('/dbquery', methods=('GET', 'POST'))
def dbquery():
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
        elif request.form['submit_button'] == 'Pull latest':
            return redirect(url_for('dbresults'))
        elif request.form['submit_button'] == "Query host":
            return redirect(url_for('hostquery'))
        else:
            pass
    return render_template('dbquery/dbquery.html')

@bp.route('/results', methods=('GET', 'POST'))
def dbresults():
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
    # initial variables.

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('dbquery'))
    else:
        #return render_template('dbquery/results.html')
        if not os.path.isfile(source_list):
            flash('No current information available.')
            flash('Please be patient while discovery is running')
            generate_list()
            all_hosts = parseHosts()
            r5 = count5()
            r6 = count6()
            r7 = count7()
            return render_template('dbquery/results.html', latestHosts=all_hosts, amountofRHEL5=r5, amountofRHEL6=r6, amountofRHEL7=r7)
        elif os.path.isfile(source_list):
            file_age = getAge()
            if file_age == 0:
                flash('file exists and is current')
                flash('Latest info pulled')
                all_hosts = parseHosts()
                r5 = count5()
                r6 = count6()
                r7 = count7()
                return render_template('dbquery/results.html', latestHosts=all_hosts, amountofRHEL5=r5, amountofRHEL6=r6, amountofRHEL7=r7)
            else:
                flash('Generating file  - please be patient')
                generate_list()
                all_hosts = parseHosts()
                r5 = count5()
                r6 = count6()
                r7 = count7()
                return render_template('dbquery/results.html', latestHosts=all_hosts, amountofRHEL5=r5, amountofRHEL6=r6, amountofRHEL7=r7)
    return render_template('dbquery/results.html', latestHosts=all_hosts, amountofRHEL5=r5, amountofRHEL6=r6, amountofRHEL7=r7)



@bp.route('/host_query', methods=('GET', 'POST'))
def hostquery():
    visibility = "visibility_off"
    global error

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

    hosts = []
    headings_list = ['Hostname','BU','Server Role','Virtual','Release version','OS','Company Code','Cost Centre' ]
    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('dbquery'))
        elif request.form['submit_button'] == 'Submit':
            gethosts = request.form.get('Host List')
            h = makelist(gethosts)
            for i in h:
                mynode = fetch_node(i)
                hosts.append(mynode)
            if error is None:
                return render_template('dbquery/host_results.html', h=hosts, ListHeadings=headings_list,setVisibility=visibility)
            elif error != None:
                flash(error)
                return render_template('dbquery/host_results.html', h=hosts, ListHeadings=headings_list,setVisibility=visibility)
    else:
        return render_template('dbquery/host_query.html')
