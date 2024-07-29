from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from penguins.auth import logout
from penguins.vsphere import vsphere_functions

# initialize variables

bp = Blueprint('vsphere_found', __name__, url_prefix='/penguins')

@bp.route('/vsphere/found_vms', methods=('GET', 'POST'))
def found_vms():

    displayVMListStatics = vsphere_functions.displayVMListStatics
    listOfVMInfoLists = session.get('list_of_VM_info_Lists')
    cantFindVMsList = session.get('cant_find_vms_list')
    foundVMsVisibility = session.get('found_vms_visibility')
    cantFindVMsVCInfoVisibility = session.get('cant_find_vms_vc_visibility')

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

    # set variable defaults
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error
    try:
        userMessageList
    except:
        userMessageList = list()

    if request.method == 'POST':
        userMessageList = list()
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('search_vms'))

    try:
        if len(userMessageList[0]) > 0:
            for message in userMessageList[0]:
                flash(message)
            userMessageList = list()
        else:
            pass
    except:
        pass

    return render_template('vsphere/found_vms.html',
        listVMStatics = displayVMListStatics,
        listVMsList = listOfVMInfoLists,
        cantFindVMsList = cantFindVMsList,
        setVMFoundVisibility = foundVMsVisibility,
        setCantFindVMsVisibility = cantFindVMsVCInfoVisibility)
