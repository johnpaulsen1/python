from flask import (
    Blueprint, redirect, render_template, request, session, url_for, Response
)
from penguins.auth import logout
from collections import defaultdict
from datetime import datetime
from time import sleep
import re
import os
import json
import ansible_runner
import logging

bp = Blueprint('ansible', __name__, url_prefix='/penguins')

# options
@bp.route('/ansible', methods=('GET', 'POST'))
def ansible_main():
    passwd_dict = {}
    clearArtifacts()
    # checks if user is logged in, if not, user will be redirected to login page
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

    role_list = roleList()
    playbooksandroles(role_list)

    json_dump = json.dumps(role_list)

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('main_options'))
        elif request.form['submit_button'] == 'Submit':
            hostlist = request.form['host_list']
            playbook = request.form['playbook']
            r = request.form['roles']
            passwd_dict['SSH']= request.form['upass']
            passwd_dict['BECOME'] = request.form['spass']

            print("plabook options - going to be used.")

            # print(hostlist, playbook, r)

            updateInventory(hostlist)
            tagstoRun(r)
            change_users(session['logged_in_user'])
            change_passwords(passwd_dict)
            # render template of ansible run view
            output = runner(playbook)
            return render_template('ansible/results.html', username=session['logged_in_user'])
        else:
            print("error")
            return render_template('ansible/error.html', username=session['logged_in_user'])
    return render_template('ansible/main.html', username=session['logged_in_user'])

def runner(playbook):
    ansible_log = os.getcwd() + '/penguins/static/ansible_log'
    if os.path.exists(ansible_log):
        os.remove(ansible_log)

    # Run the playbook.
    private_data_dir = os.getcwd() + '/penguins/ansible/plays/fnb/'
    r = ansible_runner.run(private_data_dir=private_data_dir, playbook=playbook)
    output = r.stdout.name

    os.rename(output, ansible_log)
    # with open(ansible_log, 'r') as f:
        # print(f.read())

def roleList():
    playdir = os.getcwd() + "/penguins/ansible/plays/fnb/"
    role_dict = defaultdict(list)
    for file in os.listdir(playdir):
        if ".yaml" in file:
            with open(os.path.join(playdir, file), 'r') as f:
                for line in f.readlines():
                    if "role:" in line:
                        role = line.split()[3].strip(',')
                        role_dict[file].append(role)
    return role_dict

def playbooksandroles(role_dict):
    print(os.getcwd())
    master_json = os.path.join(os.getcwd(), 'penguins/static/data.json')
    if os.path.exists(master_json):
        print("master json found.")
        os.remove(master_json)
        with open(master_json, 'w+') as f:
            json.dump(role_dict, f)
    else:
        with open(master_json, 'w+') as f:
            json.dump(role_dict, f)


def updateInventory(hostlist):
    inventory = os.path.join(os.getcwd(), 'penguins/ansible/plays/fnb/inventory/hosts')
    print(inventory)
    if os.path.exists(inventory):
        print("existing inventory found....removing...")
        os.remove(inventory)
        with open(inventory, 'w+') as f:
            f.write(hostlist)

def createTagsMaster():

    tags_master_file = os.path.join(os.getcwd(), 'penguins/ansible/plays/fnb/env/cmdline_tmp')

    template = """
--ask-become-pass
--ask-pass
"""
    with open(tags_master_file, 'w+') as f:
        f.write(template)

    f.close()

def tagstoRun(roles):
    createTagsMaster()
    env_tags = os.path.join(os.getcwd(), 'penguins/ansible/plays/fnb/env/cmdline')
    env_tags_tmp = os.path.join(os.getcwd(), 'penguins/ansible/plays/fnb/env/cmdline_tmp')
    # print(env_tags)

    if os.path.exists(env_tags):
        os.rename(env_tags_tmp, env_tags)

    with open(env_tags, 'a+') as f:
        f.write(f"--tags {roles}")

def change_users(username):
    extra_var_file = os.path.join(os.getcwd(), 'penguins/ansible/plays/fnb/env/extravars')
    extra_var_tmp_file = os.path.join(os.getcwd(), 'penguins/ansible/plays/fnb/env/extravars_tmp')
    username = "\"" + username + "\""
    if os.path.exists(extra_var_file):
        pattern = re.compile("user:")
        with open(extra_var_file, 'rt') as f:
            with open(extra_var_tmp_file, 'wt') as e:
                for line in f.readlines():
                    if pattern.search(line):
                        existing_user = re.split(":\s", line)
                        e.write(line.replace(existing_user[1], username))
                e.close()
        f.close()
    os.rename(extra_var_tmp_file,extra_var_file)

def change_passwords(password_object):
    passwd_file = os.path.join(os.getcwd(), 'penguins/ansible/plays/fnb/env/passwords')
    tmp_file = os.path.join(os.getcwd(), 'penguins/ansible/plays/fnb/env/passwords_tmp')

    for type,password in password_object.items():
        # print(f"{type}: {password}")
        new_password = "\"" + password + "\"\n"
        if os.path.exists(passwd_file):
            pattern = re.compile(type)
            with open(passwd_file, 'rt') as f:
                with open(tmp_file, 'at') as o:
                    for line in f.readlines():
                        if pattern.search(line):
                            linesplit = re.split(":\s", line)
                            base = linesplit[0]
                            old_password = linesplit[1]
                            o.write(line.replace(old_password, new_password ))
            o.close()
        f.close()
    os.rename(tmp_file, passwd_file)


def clearArtifacts():
    artifactDir = os.getcwd() + 'penguins/ansible/plays/fnb/artifacts'

    if os.path.exists(artifactDir):
        os.remove(artifactDir)
