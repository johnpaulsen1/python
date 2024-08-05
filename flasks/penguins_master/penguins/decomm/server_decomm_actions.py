from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from datetime import datetime
from penguins.auth import logout, decryptPwd, encryptPwd, domain, userDomain
from penguins.vsphere import vsphere_functions
from penguins.puppet import puppet_functions
from penguins.chef import chef_functions
from penguins.server import server_functions
from penguins.satellite_tools import satellite_functions
from penguins.flaskdb import common_functions
from penguins.other_utils import general

# initialize variables
bp = Blueprint('server_decomm_actions', __name__, url_prefix='/penguins')

co1stCharCheck = False
co2ndCharCheck = False
coIntCheck = False
coNum = str()
user = str()
userMessageList = list()

vmNICState = "disconnect"
vmDelBit = "DEL"

jumpBox = "<jump server>"

stars = "*" * 70

@bp.route('/decomm/get_decomm_servers_info', methods=('GET', 'POST'))
def decomm_server_get_info():
    # initialise variables
    error = None
    session['flash_errors'] = error
    try:
        userMessageList
    except:
        userMessageList = list()

    try:
        chef_api = chef_functions.chefAPI()
    except:
        chef_api = 'None'

    vmDeleteDate = str(general.getDecommVMDate())

    notInVsphereServersList = list()

    session['servers_found_in_puppet_list'] = list()
    session['servers_not_found_in_puppet_list'] = list()

    session['servers_found_in_chef_list'] = list()
    session['servers_not_found_in_chef_list'] = list()

    session['servers_in_vsphere_list'] = list()
    session['servers_not_in_vsphere_list'] = list()
    session['vcs_vms_in_vspheredb_dict'] = dict()

    session['list_of_servers_able_to_ssh'] = list()
    session['list_of_servers_unable_to_ssh'] = list()

    session['servers_in_satellite_list'] = list()
    session['servers_not_in_satellite_list'] = list()

    session['server_names_list'] = list()

    user = session.get('logged_in_user')
    if domain not in user:
        user = user + userDomain

    # message to be displayed to user on live messages page
    liveMessage = "user: '{}' is in on the 'Decomm Server/s' page.".format(user)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    userMessage = "Please be patient WHEN this process searches for your server/s."
    userMessageList.append([userMessage])

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
        error = None
        session['flash_errors'] = error
        userMessageList = list()
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('decomm_options'))
        elif request.form['submit_button'] == "Find Them!":
            _key = session.get('sleutel')
            encPwd = session.get('sessEncPwd')

            if request.form.get('co_number'):
                userCONum = request.form['co_number'].replace(" ", "")
                coNum = general.getCONum(userCONum)
                session['change_order_number'] = coNum
            else:
                error = "You need to enter in a valid Change Order"
                session['flash_errors'] = error

            if request.form.get('idm_password'):
                encIDMPassword = encryptPwd(request.form['idm_password'], _key)
                session['sessIDMEncPwd'] = encIDMPassword
            else:
                error = "You need to enter in your IDM password"
                session['flash_errors'] = error

            if request.form.get('vm_delete_date'):
                userVMDeleteDate = request.form['vm_delete_date'].replace(" ", "")
                session['vm_delete_date'] = userVMDeleteDate
            else:
                error = "You need to enter in a vaild delete date, using format: 'YYYY-MM-DD'"
                session['flash_errors'] = error

            if request.form.get('server_names'):
                serverNames = request.form['server_names'].replace("."+domain, "")
                serverNamesList = serverNames.split()
                session['server_names_list'] = serverNamesList
            else:
                error = "You need to enter in atleast one server name to be decommed"
                session['flash_errors'] = error

            # the below method will sort the servers into the below lists:
            # vm list, physical list, zlinux lists, kvm list
            # as well as a list of servers if can't find the virtual fact for.
            error = session.get('flash_errors')
            if error is None:
                # message to be displayed to user on live messages page
                liveMessage = "user: '{}' has requested to Decomm the below servers, with Ticket: '{}'.".format(user, coNum)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                for server in serverNamesList:
                    liveMessage = "{}".format(server)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)



                # check if servers in puppet
                puppet_functions.checkIfInPuppet(serverNamesList, user, decryptPwd(encIDMPassword, _key))
                error = session.get('flash_errors')

                if error is None:
                    # check if servers are in chef:
                    # chef_functions.checkIfInChef(serverNamesList, chef_api)
                    chef_functions.checkIfInChef(serverNamesList)

                error = session.get('flash_errors')

                if error is None:
                    # check if servers are in vsphere:
                    common_functions.queryVsphereDB(serverNamesList)
                    notInVsphereServersList = session.get('servers_not_in_vsphere_list')

                error = session.get('flash_errors')
                if len(notInVsphereServersList) > 0 and error is None:
                    # check if can access the server, for physicals / zlinux / kvms (non-vms)
                    server_functions.checkAbleToSshToServer(notInVsphereServersList, jumpBox, user, decryptPwd(encPwd, _key))

                error = session.get('flash_errors')
                if error is None:
                    # check if servers are in satellite
                    satellite_functions.checkIfServerInSatellite(serverNamesList, user, decryptPwd(encPwd, _key))

                error = session.get('flash_errors')
                if error is None:
                    # check if servers are in TMC DB
                    common_functions.queryTMCDB(serverNamesList)

            error = session.get('flash_errors')
            if error is None:
                return redirect(url_for('decomm_server_check'))

            elif error != None:
                flash(error)
                error = None
                session['flash_errors'] = error
            else:
                pass

    try:
        if len(userMessageList[0]) > 0:
            for message in userMessageList[0]:
                flash(message)
            userMessageList = list()
        else:
            pass
    except:
        pass

    return render_template('decomm/decomm_server_get_info.html',
                            vmDeleteDate = vmDeleteDate
    )



@bp.route('/decomm/check_decomm_servers', methods=('GET', 'POST'))
def decomm_server_check():
    try:
        adminAccess = session.get('admin_access')
    except:
        adminAccess = False

    try:
        new_chef_api = chef_functions.chefAPI()
    except:
        new_chef_api = 'None'

    ### Check if user is logged in, if not redirect to login page.
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if not adminAccess:
        error = "you have not been permitted to access that. Please engage with the admins if require this access."
        session['flash_errors'] = error
        return redirect(url_for('main_options'))

    # set variable defaults
    error = None
    try:
        userMessageList
    except:
        userMessageList = list()

    user = session.get('logged_in_user')
    if domain not in user:
        user = user + userDomain

    _key = session.get('sleutel')
    encPwd = session.get('sessEncPwd')
    encIDMPassword = session.get('sessIDMEncPwd')

    userMessage1 = "The decomm process may take a couple minutes, please be patient."
    userMessage2 = "You'll receive a POST decomm report when done."
    userMessage3 = "Sit back and enjoy the simplicity..."
    userMessageList.append([userMessage1, userMessage2, userMessage3])

    userVMDeleteDate = session.get('vm_delete_date')

    serverNamesDict = dict()

    inPuppetServersList = session.get('servers_found_in_puppet_list')
    notInPuppetServersList = session.get('servers_not_found_in_puppet_list')
    print("in puppet list:")
    print(inPuppetServersList)
    print()
    print("not in puppet list:")
    print(notInPuppetServersList)
    print()

    inChefServersList = session.get('servers_found_in_chef_list')
    notInChefServersList = session.get('servers_not_found_in_chef_list')
    print("in chef list:")
    print(inChefServersList)
    print()
    print("not in chef list:")
    print(notInChefServersList)
    print()

    inVsphereServersList = session.get('servers_in_vsphere_list')
    notInVsphereServersList = session.get('servers_not_in_vsphere_list')
    inVsphereDBvcsVmsDict = session.get('vcs_vms_in_vspheredb_dict')
    print("in vsphere list:")
    print(inVsphereServersList)
    print()
    print("not in vsphere list:")
    print(notInVsphereServersList)
    print()

    sshSuccessServersList = session.get('list_of_servers_able_to_ssh')
    unableToSshSuccessServersList = session.get('list_of_servers_unable_to_ssh')
    print("in ssh success list:")
    print(sshSuccessServersList)
    print()
    print("not in ssh success list:")
    print(unableToSshSuccessServersList)
    print()

    inSatelliteServersList = session.get('servers_in_satellite_list')
    notInSatelliteServersList = session.get('servers_not_in_satellite_list')
    print("in satellite list:")
    print(inSatelliteServersList)
    print()
    print("not in satellite list:")
    print(notInSatelliteServersList)
    print()

    inTMCDBServersList = session.get('servers_in_tmc_db_list')
    notInTMCDBServersList = session.get('servers_not_in_tmc_db_list')
    print("in tmc db list:")
    print(inTMCDBServersList)
    print()
    print("not in tmc db list:")
    print(notInTMCDBServersList)
    print()

    serverNamesList = session.get('server_names_list')

    for server in serverNamesList:
        inPuppet = "puppet_off"
        inChef = "chef_off"
        inVsphere = "vsphere_off"
        vmDeleteDate = userVMDeleteDate
        inSatellite = "satellite_off"
        nonVM = "physical_off"
        inTMCDB = "tmc_db_off"
        serverDetsList = list()

        if server in inPuppetServersList:
            inPuppet = "puppet_on"
            print(server, "is in puppetdb")
        elif server+"."+domain in inPuppetServersList:
            inChef = "chef_on"
            print(server, "is in puppetdb")
        else:
            inPuppet = "puppet_off"
            print(server, "is not in puppetdb")
        serverDetsList.append(inPuppet)

        if server in inChefServersList:
            inChef = "chef_on"
            print(server, "is in chef")
        elif server+"."+domain in inChefServersList:
            inChef = "chef_on"
            print(server, "is in chef")
        else:
            inChef = "chef_off"
            print(server, "is not in chef")
        serverDetsList.append(inChef)

        if server in inVsphereServersList:
            inVsphere = "vsphere_on"
            print(server, "is in vsphere")
        else:
            inVsphere = "vsphere_off"
            vmDeleteDate = inVsphere
            print(server, "is not in vsphere")
        serverDetsList.append(inVsphere)
        serverDetsList.append(vmDeleteDate)

        if server in inSatelliteServersList:
            inSatellite = "satellite_on"
            print(server, "is in satellite")
        elif server+"."+domain in inSatelliteServersList:
            inChef = "chef_on"
            print(server, "is in satellite")
        else:
            inSatellite = "satellite_off"
            print(server, "is not in satellite")
        serverDetsList.append(inSatellite)

        if server in sshSuccessServersList:
            nonVM = "physical_on"
            print(server, "is non-vm")
        elif server+"."+domain in sshSuccessServersList:
            inChef = "chef_on"
            print(server, "is non-vm")
        else:
            nonVM = "physical_off"
            print(server, "is a vm")
        serverDetsList.append(nonVM)

        if server in inTMCDBServersList:
            inTMCDB = "tmc_db_on"
            print(server, "is in tmc db")
        elif server+"."+domain in inTMCDBServersList:
            inChef = "chef_on"
            print(server, "is in tmc db")
        else:
            inTMCDB = "tmc_db_off"
            print(server, "is not in tmc db")
        serverDetsList.append(inTMCDB)

        serverNamesDict[server] = serverDetsList

    # if statement needed to decomm visibility button / check box
    decommNowVisibility = "visibility_on"


    if request.method == 'POST':
        userMessageList = list()
        if request.form.get('proceed_decomm'):
            proceedDecomm = request.form['proceed_decomm']
        else:
            proceedDecomm = None

        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('decomm_server_get_info'))

        elif request.form['submit_button'] == 'Decomm NOW!' and proceedDecomm == "proceed":
            serverDecommActionsDict = dict()
            decommPuppet = "decomm_puppet"
            decommChef = "decomm_chef"
            decommVsphere = "decomm_vsphere"
            decommSatellite = "decomm_satellite"
            decommPhysical = "decomm_physical"
            decommTMCDB = "decomm_tmc_db"
            dbName = "decommission"
            dbTableName = "decommed_hosts"
            decommPuppetServersList = list()
            decommChefServersList = list()
            decommVsphereServersList = list()
            decommSatelliteServersList = list()
            decommPhysicalServersList = list()
            decommTMCDBServersList = list()
            decommDBDict = dict()

            coNum = session.get('change_order_number')
            folderName = vmDelBit + "_" + userVMDeleteDate + "_" + coNum
            dbInsertUser = user
            if domain in dbInsertUser:
                dbInsertUser = dbInsertUser.replace(userDomain, "")

            print("*"*30)
            print(serverNamesDict)
            print("*"*30)
            for serverName, dictValues in serverNamesDict.items():
                puppetDecomm = 'N'
                chefDecomm = 'N'
                vsphereDecomm = 'N'
                vmDeleteDateDecomm = userVMDeleteDate
                satelliteDecomm = 'N'
                physicalDecomm = 'N'
                tmcDBDecomm = 'N'
                decommDBServerList = list()
                decommDBServerDictPuppet = dict()
                decommDBServerDictChef = dict()
                decommDBServerDictVsphere = dict()
                # decommDBServerDictVMDeleteDate = dict()
                decommDBServerDictSatellite = dict()
                decommDBServerDictPhysical = dict()
                decommDBServerDictTMCDB = dict()

                # message to be displayed to user on live messages page
                liveMessage = "server name: '{}'.".format(serverName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
                
                print("dictValues:")
                print(dictValues)

                for listValue in dictValues:
                    decommCheckBoxName = serverName + "-" + listValue
                    # decommCheckBoxValue = request.form[decommCheckBoxName]
                    try:
                        decommCheckBoxValue = request.form.get(decommCheckBoxName)
                    except Exception as e:
                        decommCheckBoxValue = None
                        print("Exception:")
                        general.showUserMessage("Exception:")
                        print(e)
                        general.showUserMessage(str(e))
                    vmDeleteDateTextField = 'vm_delete_date_' + serverName
                    
                    if decommCheckBoxValue:
                        try:
                            if 'puppet' in decommCheckBoxName and 'on' in decommCheckBoxValue:

                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' decomm puppet.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                try:
                                    decommPuppetServersList = serverDecommActionsDict.get(decommPuppet)
                                except:
                                    pass
                                if decommPuppetServersList == None:
                                    decommPuppetServersList = list()
                                decommPuppetServersList.append(serverName)
                                serverDecommActionsDict[decommPuppet] = decommPuppetServersList
                            elif 'puppet' in decommCheckBoxName and ('off' in decommCheckBoxValue or decommCheckBoxValue == None):
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm puppet.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictPuppet['puppet_decommed'] = puppetDecomm
                                decommDBServerList.append(decommDBServerDictPuppet)
                                decommDBDict[serverName] = decommDBServerList

                            if 'chef' in decommCheckBoxName and 'on' in decommCheckBoxValue:

                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' decomm chef.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                try:
                                    decommChefServersList = serverDecommActionsDict.get(decommChef)
                                except:
                                    pass
                                if decommChefServersList == None:
                                    decommChefServersList = list()
                                decommChefServersList.append(serverName)
                                serverDecommActionsDict[decommChef] = decommChefServersList
                            elif 'chef' in decommCheckBoxName and ('off' in decommCheckBoxValue or decommCheckBoxValue == None):

                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm chef.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictChef['chef_decommed'] = chefDecomm
                                decommDBServerList.append(decommDBServerDictChef)
                                decommDBDict[serverName] = decommDBServerList

                            if 'vsphere' in decommCheckBoxName and 'on' in decommCheckBoxValue:
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' decomm vsphere.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)
                                try:
                                    vmDeleteDateValue = request.form[vmDeleteDateTextField]
                                    serverName = serverName.split('.')[0]
                                    try:
                                        decommDBServerDictVMDeleteDate
                                    except:
                                        decommDBServerDictVMDeleteDate = dict()

                                    decommDBServerDictVMDeleteDate[serverName] = vmDeleteDateValue

                                    decommVsphereServersList = serverDecommActionsDict.get(decommVsphere)
                                except:
                                    pass
                                if decommVsphereServersList == None:
                                    decommVsphereServersList = list()
                                decommVsphereServersList.append(serverName)
                                serverDecommActionsDict[decommVsphere] = decommVsphereServersList
                            elif 'vsphere' in decommCheckBoxName and ('off' in decommCheckBoxValue or decommCheckBoxValue == None):
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm vsphere.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictVsphere['vsphere_decommed'] = vsphereDecomm
                                decommDBServerList.append(decommDBServerDictVsphere)
                                decommDBDict[serverName] = decommDBServerList

                            if 'satellite' in decommCheckBoxName and 'on' in decommCheckBoxValue:
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' decomm satellite.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)
                                try:
                                    decommSatelliteServersList = serverDecommActionsDict.get(decommSatellite)
                                except:
                                    pass
                                if decommSatelliteServersList == None:
                                    decommSatelliteServersList = list()
                                decommSatelliteServersList.append(serverName)
                                serverDecommActionsDict[decommSatellite] = decommSatelliteServersList
                            elif 'satellite' in decommCheckBoxName and ('off' in decommCheckBoxValue or decommCheckBoxValue == None):
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm satellite.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictSatellite['satellite_decommed'] = satelliteDecomm
                                decommDBServerList.append(decommDBServerDictSatellite)
                                decommDBDict[serverName] = decommDBServerList

                            if 'physical' in decommCheckBoxName and 'on' in decommCheckBoxValue:
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' decomm Physical.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)
                                try:
                                    decommPhysicalServersList = serverDecommActionsDict.get(decommPhysical)
                                except:
                                    pass
                                if decommPhysicalServersList == None:
                                    decommPhysicalServersList = list()
                                decommPhysicalServersList.append(serverName)
                                serverDecommActionsDict[decommPhysical] = decommPhysicalServersList
                            elif 'physical' in decommCheckBoxName and ('off' in decommCheckBoxValue or decommCheckBoxValue == None):
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm Physical.".format(serverName)
                                print(liveMessage)
                                print()

                                decommDBServerDictPhysical['physical_decommed'] = physicalDecomm
                                decommDBServerList.append(decommDBServerDictPhysical)
                                decommDBDict[serverName] = decommDBServerList

                            if 'tmc_db' in decommCheckBoxName and 'on' in decommCheckBoxValue:
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' decomm TMC DB.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)
                                try:
                                    decommTMCDBServersList = serverDecommActionsDict.get(decommTMCDB)
                                except:
                                    pass
                                if decommTMCDBServersList == None:
                                    decommTMCDBServersList = list()
                                decommTMCDBServersList.append(serverName)
                                serverDecommActionsDict[decommTMCDB] = decommTMCDBServersList
                            elif 'tmc_db' in decommCheckBoxName and ('off' in decommCheckBoxValue or decommCheckBoxValue == None):
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm TMC DB.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictTMCDB['tmc_db_decommed'] = tmcDBDecomm
                                decommDBServerList.append(decommDBServerDictTMCDB)
                                decommDBDict[serverName] = decommDBServerList
                        except Exception as e:
                            print("Exception:")
                            general.showUserMessage("Exception:")
                            print(e)
                            general.showUserMessage(str(e))

                    else:
                        try:
                            if 'puppet' in decommCheckBoxName:
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm puppet.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictPuppet['puppet_decommed'] = puppetDecomm
                                decommDBServerList.append(decommDBServerDictPuppet)
                                decommDBDict[serverName] = decommDBServerList

                            if 'chef' in decommCheckBoxName:
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm chef.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictChef['chef_decommed'] = chefDecomm
                                decommDBServerList.append(decommDBServerDictChef)
                                decommDBDict[serverName] = decommDBServerList

                            if 'vsphere' in decommCheckBoxName:
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm vsphere.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictVsphere['vsphere_decommed'] = vsphereDecomm
                                decommDBServerList.append(decommDBServerDictVsphere)
                                decommDBDict[serverName] = decommDBServerList

                            if 'satellite' in decommCheckBoxName:
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm satellite.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictSatellite['satellite_decommed'] = satelliteDecomm
                                decommDBServerList.append(decommDBServerDictSatellite)
                                decommDBDict[serverName] = decommDBServerList

                            if 'physical' in decommCheckBoxName:
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm physical.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictPhysical['physical_decommed'] = physicalDecomm
                                decommDBServerList.append(decommDBServerDictPhysical)
                                decommDBDict[serverName] = decommDBServerList

                            if 'tmc_db' in decommCheckBoxName:
                                # message to be displayed to user on live messages page
                                liveMessage = "server: '{}' DO NOT decomm TMC DB.".format(serverName)
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                decommDBServerDictTMCDB['tmc_db_decommed'] = tmcDBDecomm
                                decommDBServerList.append(decommDBServerDictTMCDB)
                                decommDBDict[serverName] = decommDBServerList
                        except Exception as e:
                            print("Exception:")
                            general.showUserMessage("Exception:")
                            print(e)
                            general.showUserMessage(str(e))

            print()
            if decommDBDict:
                pass
            else:
                decommDBDict = dict()

            # perform decomm actions, per dictionary key.
            for dictKey, dictValue in serverDecommActionsDict.items():
                puppetDecomm = 'N'
                chefDecomm = 'N'
                vsphereDecomm = 'N'
                vmDeleteDateDecomm = userVMDeleteDate
                satelliteDecomm = 'N'
                physicalDecomm = 'N'
                tmcDBDecomm = 'N'

                decommDBServerDictPuppet = dict()
                decommDBServerDictChef = dict()
                decommDBServerDictVsphere = dict()
                decommDBServerDictSatellite = dict()
                decommDBServerDictPhysical = dict()
                decommDBServerDictTMCDB = dict()
                print()

                # puppet decomm actions:
                if dictKey == "decomm_puppet":
                    # message to be displayed to user on live messages page
                    liveMessage = "{}".format(stars)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "function to decomm: '{}'".format(dictKey)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "server/s: '{}'".format(dictValue)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    try:
                        puppet_functions.puppetDecommActions(dictValue, user, decryptPwd(encPwd, _key), decryptPwd(encIDMPassword, _key), coNum)
                        puppetDecomm = 'Y'
                        for server in dictValue:
                            try:
                                decommDBServerList = decommDBDict.get(server)
                                if decommDBServerList == None:
                                    decommDBServerList = list()
                            except:
                                decommDBServerList = list()
                                puppetDecomm = 'F'

                            decommDBServerDictPuppet['puppet_decommed'] = puppetDecomm
                            decommDBServerList.append(decommDBServerDictPuppet)
                            decommDBDict[server] = decommDBServerList

                    except Exception as e:
                        # message to be displayed to user on live messages page
                        print("Exception:")
                        general.showUserMessage("Exception:")
                        print(e)
                        general.showUserMessage(str(e))

                        error = "possible error may have occurred when decomming the below server/s out of puppet."
                        print(error)
                        print()
                        general.showUserMessage(error)

                        liveMessage = "servers: '{}'".format(dictValue)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                        liveMessage = "please manually check that they've been decommed out of puppet."
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                # chef decomm actions:
                if dictKey == "decomm_chef":
                    # message to be displayed to user on live messages page
                    liveMessage = "{}".format(stars)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "function to decomm: '{}'".format(dictKey)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "server/s: '{}'".format(dictValue)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    try:
                        # chef_functions.deleteChefNodes(dictValue, new_chef_api)
                        chef_functions.deleteChefNodes(dictValue)
                        chefDecomm = 'Y'
                        for server in dictValue:
                            try:
                                decommDBServerList = decommDBDict.get(server)
                                if decommDBServerList == None:
                                    decommDBServerList = list()
                            except:
                                decommDBServerList = list()
                                chefDecomm = 'F'

                            decommDBServerDictChef['chef_decommed'] = chefDecomm
                            decommDBServerList.append(decommDBServerDictChef)
                            decommDBDict[server] = decommDBServerList

                    except Exception as e:
                        # message to be displayed to user on live messages page
                        print("Exception:")
                        general.showUserMessage("Exception:")
                        print(e)
                        general.showUserMessage(str(e))

                        error = "possible error may have occurred when decomming the below server/s out of chef."
                        print(error)
                        print()
                        general.showUserMessage(error)

                        liveMessage = "servers: '{}'".format(dictValue)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                        liveMessage = "please manually check that they've been decommed out of chef."
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                # vsphere decomm actions:
                if dictKey == "decomm_vsphere":
                    # message to be displayed to user on live messages page
                    liveMessage = "{}".format(stars)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "function to decomm: '{}'".format(dictKey)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "server/s: '{}'".format(dictValue)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    vcsVmsToDecommDict = dict()
                    for vc, vmsList in inVsphereDBvcsVmsDict.items():
                        vmsToDecommList = list()
                        for selectedVM in dictValue:
                            if selectedVM in vmsList:
                                vmsToDecommList.append(selectedVM)
                        vcsVmsToDecommDict[vc] = vmsToDecommList

                    # print(vcsVmsToDecommDict)
                    try:
                        vmVsphereInstancesList = vsphere_functions.getVMvSphereInstancesWithVC(user, decryptPwd(encPwd, _key), vcsVmsToDecommDict)
                        vmObjsList = vmVsphereInstancesList[0]
                        dcObjsList = vmVsphereInstancesList[1]
                        siList = vmVsphereInstancesList[2]
                        vsphere_functions.vmDecommActions(decommDBServerDictVMDeleteDate, dcObjsList, siList, vmObjsList, vmNICState)
                        vsphereDecomm = 'Y'
                        for server in dictValue:
                            vmDeleteDateDecomm = decommDBServerDictVMDeleteDate[server]
                            try:
                                decommDBServerList = decommDBDict.get(server)
                                if decommDBServerList == None:
                                    decommDBServerList = list()
                            except:
                                decommDBServerList = list()
                                vsphereDecomm = 'F'

                            decommDBServerDictVsphere['vsphere_decommed'] = vsphereDecomm
                            decommDBServerList.append(decommDBServerDictVsphere)
                            decommDBDict[server] = decommDBServerList

                    except Exception as e:
                        # message to be displayed to user on live messages page
                        print("Exception:")
                        general.showUserMessage("Exception:")
                        print(e)
                        general.showUserMessage(str(e))

                        error = "possible error may have occurred when decomming the below server/s out of vsphere."
                        print(error)
                        print()
                        general.showUserMessage(error)

                        liveMessage = "servers: '{}'".format(dictValue)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                        liveMessage = "please manually check that they've been decommed out of vsphere."
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                # satellite decomm actions
                if dictKey == "decomm_satellite":
                    # message to be displayed to user on live messages page
                    liveMessage = "{}".format(stars)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "function to decomm: '{}'".format(dictKey)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "server/s: '{}'".format(dictValue)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    try:
                        satellite_functions.satelliteDecommActions(dictValue, user, decryptPwd(encPwd, _key))
                        satelliteDecomm = 'Y'
                        for server in dictValue:
                            try:
                                decommDBServerList = decommDBDict.get(server)
                                if decommDBServerList == None:
                                    decommDBServerList = list()
                            except:
                                decommDBServerList = list()
                                satelliteDecomm = 'F'

                            decommDBServerDictSatellite['satellite_decommed'] = satelliteDecomm
                            decommDBServerList.append(decommDBServerDictSatellite)
                            decommDBDict[server] = decommDBServerList

                    except Exception as e:
                        # message to be displayed to user on live messages page
                        print("Exception:")
                        general.showUserMessage("Exception:")
                        print(e)
                        general.showUserMessage(str(e))

                        error = "possible error may have occurred when decomming the below server/s out of satellite."
                        print(error)
                        print()
                        general.showUserMessage(error)

                        liveMessage = "servers: '{}'".format(dictValue)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                        liveMessage = "please manually check that they've been decommed out of satellite."
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                # physical servers decomm actions
                if dictKey == "decomm_physical":
                    # message to be displayed to user on live messages page
                    liveMessage = "{}".format(stars)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "function to decomm: '{}'".format(dictKey)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "server/s: '{}'".format(dictValue)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)
                    try:
                        server_functions.powerDownPhysicals(jumpBox, dictValue, user, decryptPwd(encPwd, _key))
                        physicalDecomm = 'Y'
                        for server in dictValue:
                            try:
                                decommDBServerList = decommDBDict.get(server)
                                if decommDBServerList == None:
                                    decommDBServerList = list()
                            except:
                                decommDBServerList = list()
                                physicalDecomm = 'F'

                            decommDBServerDictPhysical['physical_decommed'] = physicalDecomm
                            decommDBServerList.append(decommDBServerDictPhysical)
                            decommDBDict[server] = decommDBServerList

                    except Exception as e:
                        # message to be displayed to user on live messages page
                        print("Exception:")
                        general.showUserMessage("Exception:")
                        print(e)
                        general.showUserMessage(str(e))

                        error = "possible error may have occurred when powering down the below 'physical' servers."
                        print(error)
                        print()
                        general.showUserMessage(error)

                        liveMessage = "servers: '{}'".format(dictValue)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                        liveMessage = "please manually check that they've been powered down."
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                # TMC DB decomm actions
                if dictKey == "decomm_tmc_db":
                    # message to be displayed to user on live messages page
                    liveMessage = "{}".format(stars)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "function to decomm: '{}'".format(dictKey)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    liveMessage = "server/s: '{}'".format(dictValue)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    for server in dictValue:
                        try:
                            common_functions.cleanupTMCDB(server)
                            tmcDBDecomm = 'Y'
                            decommDBServerList = decommDBDict.get(server)
                            if decommDBServerList == None:
                                decommDBServerList = list()
                        except Exception as e:
                            decommDBServerList = list()
                            tmcDBDecomm = 'F'

                            # message to be displayed to user on live messages page
                            print("Exception:")
                            general.showUserMessage("Exception:")
                            print(e)
                            general.showUserMessage(str(e))

                            error = "possible error may have occurred when decomming the below server/s out of tmc db."
                            print(error)
                            print()
                            general.showUserMessage(error)

                            liveMessage = "servers: '{}'".format(dictValue)
                            print(liveMessage)
                            print()
                            general.showUserMessage(liveMessage)

                            liveMessage = "please manually check that they've been decommed out of tmc db."
                            print(liveMessage)
                            print()
                            general.showUserMessage(liveMessage)

                        decommDBServerDictTMCDB['tmc_db_decommed'] = tmcDBDecomm
                        decommDBServerList.append(decommDBServerDictTMCDB)
                        decommDBDict[server] = decommDBServerList


            # method to verify decomm actions, to popolate DB post decomm
            error = session.get('flash_errors')
            if error == None:
                activeStatus = "Currently active"
                deactivatedStatus = "Deactivated"

                puppetColumnName = "puppet_decommed"
                puppetColumnValue = '\'N\''
                mustDecommPuppet = False

                chefColumnName = "chef_decommed"
                chefColumnValue = '\'N\''
                mustDecommChef = False

                vsphereColumnName = "vsphere_decommed"
                vsphereColumnValue = '\'N\''
                mustDecommVsphere = False

                satelliteColumnName = "satellite_decommed"
                satelliteColumnValue = '\'N\''
                mustDecommSatellite = False

                physicalColumnName = "physical_decommed"
                physicalColumnValue = '\'N\''
                mustDecommPhysical = False

                tmcDBColumnName = "tmc_db_decommed"
                tmcDBColumnValue = '\'N\''
                mustDecommTMCDB = False

                user = session.get('logged_in_user')
                encIDMPassword = session.get('sessIDMEncPwd')
                encPwd = session.get('sessEncPwd')

                for dictKey, dictValue in decommDBDict.items():
                    serverName = dictKey
                    insertQuery = str()
                    dateTime = datetime.now()
                    for dictColumn in dictValue:
                        for decommActionName, decommActionValue in dictColumn.items():
                            print(decommActionName, ":", decommActionValue)

                            if decommActionName == puppetColumnName and decommActionValue == "Y":
                                # message to be displayed to user on live messages page
                                liveMessage = "verify puppet decomm"
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                # verify puppet decomm for server
                                try:
                                    puppetDecommStatus = puppet_functions.verifyPuppetDecomm(serverName, user, decryptPwd(encIDMPassword, _key))
                                except:
                                    puppetDecommStatus = str()
                                    puppetColumnValue = '\'F\''
                                if puppetDecommStatus == deactivatedStatus:
                                    puppetColumnValue = '\'Y\''
                                    mustDecommPuppet = True
                                elif puppetDecommStatus == activeStatus:
                                    puppetColumnValue = '\'F\''
                                    mustDecommPuppet = True
                            elif decommActionName == puppetColumnName and decommActionValue == "N":
                                puppetColumnValue = '\'N\''
                                mustDecommPuppet = False
                            elif decommActionName == puppetColumnName and decommActionValue == "F":
                                puppetColumnValue = '\'F\''
                                mustDecommPuppet = True


                            if decommActionName == chefColumnName and decommActionValue == "Y":
                                # message to be displayed to user on live messages page
                                liveMessage = "verify chef decomm"
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                # verify chef decomm for server
                                try:
                                    chefDecommStatus = chef_functions.verifyChefDecomm(serverName)
                                except:
                                    chefDecommStatus = str()
                                    chefColumnValue = '\'F\''
                                    mustDecommChef = True
                                if chefDecommStatus == deactivatedStatus:
                                    chefColumnValue = '\'Y\''
                                    mustDecommChef = True
                                elif chefDecommStatus == activeStatus:
                                    chefColumnValue = '\'F\''
                                    mustDecommChef = True
                            elif decommActionName == chefColumnName and decommActionValue == "N":
                                chefColumnValue = '\'N\''
                                mustDecommChef = False
                            elif decommActionName == chefColumnName and decommActionValue == "F":
                                chefColumnValue = '\'F\''
                                mustDecommChef = True


                            if decommActionName == vsphereColumnName and decommActionValue == "Y":
                                # message to be displayed to user on live messages page
                                liveMessage = "verify vsphere decomm"
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                for vmObj in vmObjsList:
                                    vmName = vmObj.config.name
                                    if vmName == serverName:
                                        # verify vsphere decomm for server
                                        try:
                                            vsphereDecommStatus = vsphere_functions.verifyVsphereDecomm(vmObj, decommDBServerDictVMDeleteDate)
                                        except:
                                            vsphereDecommStatus = str()
                                            vsphereColumnValue = '\'F\''
                                            mustDecommVsphere = True
                                        if vsphereDecommStatus == deactivatedStatus:
                                            vsphereColumnValue = '\'Y\''
                                            mustDecommVsphere = True

                                            # step to clean up vsphere database
                                            # run query to get and delete vm out of vpshere db
                                            try:
                                                common_functions.cleanupVsphereDB(vmName)

                                            except Exception as e:
                                                # message to be displayed to user on live messages page
                                                print("Exception:")
                                                general.showUserMessage("Exception:")
                                                print(str(e))
                                                print()
                                                general.showUserMessage(str(e))


                                        elif vsphereDecommStatus == activeStatus:
                                            vsphereColumnValue = '\'F\''
                                            mustDecommVsphere = True
                                        break
                            elif decommActionName == vsphereColumnName and decommActionValue == "N":
                                vsphereColumnValue = '\'N\''
                                mustDecommVsphere = False
                            elif decommActionName == vsphereColumnName and decommActionValue == "F":
                                vsphereColumnValue = '\'F\''
                                mustDecommVsphere = True

                            if decommActionName == satelliteColumnName and decommActionValue == "Y":
                                # message to be displayed to user on live messages page
                                liveMessage = "verify satellite decomm"
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                # verify satellite decomm for server
                                try:
                                    satelliteDecommStatus = satellite_functions.verifySatelliteDecomm(serverName, user, decryptPwd(encPwd, _key))
                                except:
                                    satelliteDecommStatus = str()
                                    satelliteColumnValue = '\'F\''
                                    mustDecommSatellite = True
                                if satelliteDecommStatus == deactivatedStatus:
                                    satelliteColumnValue = '\'Y\''
                                    mustDecommSatellite = True
                                elif satelliteDecommStatus == activeStatus:
                                    satelliteColumnValue = '\'F\''
                                    mustDecommSatellite = True
                            elif decommActionName == satelliteColumnName and decommActionValue == "N":
                                satelliteColumnValue = '\'N\''
                                mustDecommSatellite = False
                            elif decommActionName == satelliteColumnName and decommActionValue == "F":
                                satelliteColumnValue = '\'F\''
                                mustDecommSatellite = True

                            if decommActionName == physicalColumnName and decommActionValue == "Y":
                                # message to be displayed to user on live messages page
                                liveMessage = "verify 'physical' decomm"
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                # verify physical decomm for server
                                try:
                                    physicalDecommStatus = server_functions.verifyPhysicalDecomm(serverName, user, decryptPwd(encPwd, _key), jumpBox)
                                except:
                                    physicalDecommStatus = str()
                                    physicalColumnValue = '\'F\''
                                    mustDecommPhysical = True
                                if physicalDecommStatus == deactivatedStatus:
                                    physicalColumnValue = '\'Y\''
                                    mustDecommPhysical = True
                                elif physicalDecommStatus == activeStatus:
                                    physicalColumnValue = '\'F\''
                                    mustDecommPhysical = True
                            elif decommActionName == physicalColumnName and decommActionValue == "N":
                                physicalColumnValue = '\'N\''
                                mustDecommPhysical = False
                            elif decommActionName == physicalColumnName and decommActionValue == "F":
                                physicalColumnValue = '\'F\''
                                mustDecommPhysical = True

                            if decommActionName == tmcDBColumnName and decommActionValue == "Y":
                                # message to be displayed to user on live messages page
                                liveMessage = "verify TMC DB decomm"
                                print(liveMessage)
                                print()
                                general.showUserMessage(liveMessage)

                                # verify tmc DB decomm for server
                                try:
                                    tmcDBDecommStatus = common_functions.verifyTMCDBDecomm(serverName)
                                except:
                                    tmcDBDecommStatus = str()
                                    tmcDBColumnValue = '\'F\''
                                    mustDecommTMCDB = True
                                if tmcDBDecommStatus == deactivatedStatus:
                                    tmcDBColumnValue = '\'Y\''
                                    mustDecommTMCDB = True
                                elif tmcDBDecommStatus == activeStatus:
                                    tmcDBColumnValue = '\'F\''
                                    mustDecommTMCDB = True
                            elif decommActionName == tmcDBColumnName and decommActionValue == "N":
                                tmcDBColumnValue = '\'N\''
                                mustDecommTMCDB = False
                            elif decommActionName == tmcDBColumnName and decommActionValue == "F":
                                tmcDBColumnValue = '\'F\''
                                mustDecommTMCDB = True

                    if mustDecommPuppet or mustDecommChef or mustDecommVsphere or mustDecommSatellite or mustDecommPhysical or mustDecommTMCDB:
                        insertQuery = "INSERT INTO {} ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES ('{}', '{}', '{}', {}, {}, {}, {}, {}, {}, '{}');".format(
                                        dbTableName,
                                        "date_time_actioned",
                                        "change_number",
                                        "host_name",
                                        puppetColumnName,
                                        chefColumnName,
                                        vsphereColumnName,
                                        satelliteColumnName,
                                        physicalColumnName,
                                        tmcDBColumnName,
                                        "actioned_by",
                                        dateTime,
                                        coNum,
                                        serverName,
                                        puppetColumnValue,
                                        chefColumnValue,
                                        vsphereColumnValue,
                                        satelliteColumnValue,
                                        physicalColumnValue,
                                        tmcDBColumnValue,
                                        dbInsertUser
                        )

                        # insert decomm data into decomm DB table
                        try:
                            common_functions.dbQueryExecutor(dbName, insertQuery)
                            # message to be displayed to user on live messages page
                            liveMessage = "{}".format(stars)
                            print(liveMessage)
                            print()
                            general.showUserMessage(liveMessage)

                        except Exception as e:
                            # message to be displayed to user on live messages page
                            print("Exception:")
                            general.showUserMessage("Exception:")
                            print(str(e))
                            print()
                            general.showUserMessage(str(e))

                return redirect(url_for('decomm_report'))

            elif error != None:
                flash(error)
                error = None
                session['flash_errors'] = error

        elif request.form['submit_button'] == 'Decomm NOW!' and proceedDecomm != "proceed":
            error = "You need to CHECK the checkbox above, in order to proceed with the decommission process"
            flash(error)
            error = None
            return redirect(url_for('decomm_server_check'))
        else:
            pass

    try:
        if len(userMessageList[0]) > 0 and decommNowVisibility == "visibility_on":
            for message in userMessageList[0]:
                flash(message)
            userMessageList = list()
        else:
            pass
    except:
        pass

    return render_template('decomm/decomm_server_check.html',
        serversDict = serverNamesDict,
        setDecommNowVisibility = decommNowVisibility,
        vmDeleteDate = userVMDeleteDate)
