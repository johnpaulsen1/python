from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from cryptography.fernet import Fernet
from penguins.auth import logout, decryptPwd
from penguins.vsphere import vsphere_functions
from penguins.son_of import anton

bp = Blueprint('vsphere_search', __name__, url_prefix='/penguins')

vmHostnamesList = list()
domain = "<domain>"

@bp.route('/vsphere/search_vms', methods=('GET', 'POST'))
def search_vms():

    # initialise variables
    try:
        error = session.get('flash_errors')
    except Exception as e:
        print("Exception caught: '{}'".format(str(e)))
        error = None
        session['flash_errors'] = error
    search_option = "hostname"
    userMessageList = list()
    session['list_of_VM_info_Lists'] = list()
    session['cant_find_vms_list'] = list()
    session['found_vcs_list'] = list()
    session['found_vms_visibility'] = "visibility_off"
    session['cant_find_vms_vc_visibility'] = "visibility_off"

    # message to be displayed to user on next page
    userMessage = "Please be patient WHEN this process searches for your vm/s."
    userMessageList.append([userMessage])

    try:
        adminAccess = session.get('admin_access')
    except Exception as e:
        print("Exception caught: '{}'".format(str(e)))
        adminAccess = False

    ### Check if user is logged in, if not redirect to login page.
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not adminAccess:
        error = "you have not been permitted to access that. Please engage with the admins if require this access."
        session['flash_errors'] = error
        return redirect(url_for('main_options'))

    if request.method == 'POST':
        try:
            error = session.get('flash_errors')
        except Exception as e:
            print("Exception caught: '{}'".format(str(e)))
            error = None
            session['flash_errors'] = error
        userMessageList = list()
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('vsphere_options'))
        elif request.form['submit_button'] == "Search!":
            _key = session.get('sleutel')
            user = session.get('logged_in_user')
            if domain not in user:
                user = user + "@{}".format(domain)
            encPwd = session.get('sessEncPwd')
            search_option = request.form['vm_search_by']
            vmSearchField = request.form['vm_search_field']

            if vmSearchField == "" and search_option == 'hostname':
                error = "You need to enter in at least one " + search_option + " to search"
                session['flash_errors'] = error
            elif vmSearchField == "" and search_option == 'MAC address':
                error = "You need to enter in at least one " + search_option + " to search"
                session['flash_errors'] = error

            if search_option == 'hostname':
                setError = False
                colonCount = 0
                vmMacAddressesList = list()
                vmIPAddressesList = list()
                vmHostnames = vmSearchField
                vmHostnamesList = vmHostnames.split()

                for vmHostname in vmHostnamesList:
                    colonCount = vmHostname.count(':')

                    if colonCount > 0:
                        setError = True
                        break;

                    if setError == False:
                        for char in vmHostname:
                            if char.isalpha() == True:
                                setError = False
                                break;
                            elif char.isalpha() == False:
                                setError = True

                if setError == True:
                    error = "one or more invalid " + search_option + "/s entered, try again please"
                    session['flash_errors'] = error

            elif search_option == 'MAC address':
                setError = False
                colonCount = 0
                vmHostnamesList = list()
                vmIPAddressesList = list()
                vmMacAddresses = vmSearchField
                vmMacAddressesList = vmMacAddresses.split()

                for vmMacAddress in vmMacAddressesList:
                    colonCount = vmMacAddress.count(':')
                    if colonCount != 5:
                        setError = True

                if setError == True:
                    error = "one or more invalid " + search_option + "/s entered, try again please"
                    session['flash_errors'] = error

            elif search_option == 'IP address':
                setError = False
                colonCount = 0
                vmHostnamesList = list()
                vmMacAddressesList = list()
                vmIPAddresses = vmSearchField
                vmIPAddressesList = vmIPAddresses.split()

                for vmIPAddress in vmIPAddressesList:
                    periodCount = vmIPAddress.count('.')
                    colonCount = vmIPAddress.count(':')

                    if periodCount != 3:
                        setError = True
                        break;

                    if colonCount > 0:
                        setError = True
                        break;

                    if setError == False:
                        numsOnlyVMIPAddress = vmIPAddress.replace('.','')
                        for num in numsOnlyVMIPAddress:
                            if num.isnumeric() == False:
                                setError = True
                                break;
                            elif num.isnumeric() == True:
                                setError = False

                if setError == True:
                    error = "one or more invalid " + search_option + "/s entered, try again please"
                    session['flash_errors'] = error

            # actions for vm servers
            if len(vmHostnamesList) > 0 and error is None:
                try:
                    auth_list = anton.getTheSecretSauce()
                    cipher_suite = Fernet(auth_list[1])
                    vmVsphereInstancesList = vsphere_functions.getVMvSphereInstances(
                        cipher_suite.decrypt(auth_list[0]).decode(),
                        cipher_suite.decrypt(auth_list[2]).decode(),
                        vmHostnamesList)
                    vmObjsList = vmVsphereInstancesList[0]
                    print()
                    print(vmObjsList)
                    print()
                except Exception as e:
                    print("Exception caught: '{}'".format(str(e)))
                    vmObjsList = list()
                    error = "Failure occured in retrieving vm object/s for vm/s: '{}'".format(str(vmHostnamesList))

            if len(vmMacAddressesList) > 0 and error is None:
                try:
                    auth_list = anton.getTheSecretSauce()
                    cipher_suite = Fernet(auth_list[1])
                    allVmObjsList = vsphere_functions.getAllVMInstances(
                        cipher_suite.decrypt(auth_list[0]).decode(),
                        cipher_suite.decrypt(auth_list[2]).decode())
                    vmObjsList = vsphere_functions.getVMInstanceByMAC(allVmObjsList, vmMacAddressesList)
                except Exception as e:
                    print("Exception caught: '{}'".format(str(e)))
                    vmObjsList = list()
                    error = "Failure occured in retrieving vm object/s for MAC: '{}'".format(str(vmMacAddressesList))

            if len(vmIPAddressesList) > 0 and error is None:
                try:
                    auth_list = anton.getTheSecretSauce()
                    cipher_suite = Fernet(auth_list[1])
                    allVmObjsList = vsphere_functions.getAllVMInstances(
                        cipher_suite.decrypt(auth_list[0]).decode(),
                        cipher_suite.decrypt(auth_list[2]).decode())
                    vmObjsList = vsphere_functions.getVMInstanceByIP(allVmObjsList, vmIPAddressesList)
                except Exception as e:
                    print("Exception caught: '{}'".format(str(e)))
                    vmObjsList = list()
                    error = "Failure occured in retrieving vm object/s for IP: '{}'".format(str(vmIPAddressesList))

            if error is None:
                # actions for vm servers
                if len(vmHostnamesList) > 0 or len(vmMacAddressesList) > 0 or len(vmIPAddressesList) > 0:
                    try:
                        vsphere_functions.displayVMs(vmObjsList)
                    except Exception as e:
                        print("Exception caught: '{}'".format(str(e)))

                return redirect(url_for('found_vms'))

            elif error != None:
                flash(error)
                error = None
            else:
                pass

    try:
        if len(userMessageList[0]) > 0:
            for message in userMessageList[0]:
                flash(message)
            userMessageList = list()
        else:
            pass
    except Exception as e:
        print("Exception caught: '{}'".format(str(e)))

    return render_template('vsphere/search_vms.html')
