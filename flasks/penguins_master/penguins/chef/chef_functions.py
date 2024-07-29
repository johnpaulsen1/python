import chef
from chef import Node
from flask import session
import os
from penguins.auth import domain, userDomain
from penguins.server import server_functions
from penguins.other_utils import general
from time import sleep

stars = "*" * 70
chefKnifeFileLocation = '/opt/flask/.chef/knife.rb'

def checkIfInChef(serversList):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Check if Server in Chef Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    inChefServersList = list()
    notInChefServersList = list()

    for server in serversList:
        liveMessage = "checking if server: '{}' is in chef.".format(server)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        # server = server.lower()
        # remove "<domain>" from server name so that it'll match in the puppet query for "hostname"
        if domain in server:
            thisServer = server.replace("<domain>","")
        else:
            thisServer = server
        # print(server)

        # run local cmd on flask server to check if server is in chef
        try:
            checkInChefCmd = os.system('/bin/knife node list -c {} | /bin/grep -i {}'.format(chefKnifeFileLocation, thisServer))
            exitCode = os.WEXITSTATUS(checkInChefCmd)
        except Exception as e:
            error = "unable to run knife command locally to check if server: '{}' is in chef or not.".format(server)
            print(error)
            print()
            general.showUserMessage(error)
            print("Exception:")
            print(e)
            general.showUserMessage("Exception:")
            general.showUserMessage(str(e))
            general.showUserMessage(".")
            exitCode = 1
        
        if exitCode == 0:
            inChefServersList.append(server)
            liveMessage = "server: '{}' is in chef.".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            general.showUserMessage(".")
        else:
            notInChefServersList.append(server)
            liveMessage = "server: '{}' is NOT in chef.".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            general.showUserMessage(".")
    
    # remove duplicates from the list, if there are.
    if len(inChefServersList) > 0:
        inChefServersList = removeDuplicatesInList(inChefServersList)
        session['servers_found_in_chef_list'] = inChefServersList
    if len(notInChefServersList) > 0:
        notInChefServersList = removeDuplicatesInList(notInChefServersList)
        session['servers_not_found_in_chef_list'] = notInChefServersList


def deleteChefNodes(serversList):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Delete Server/s on Chef Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    inChefServersList = list()
    notInChefServersList = list()

    for server in serversList:
        liveMessage = "attempting to delete server: '{}' from chef.".format(server)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        # server = server.lower()
        # remove "<domain>" from server name so that it'll match in the puppet query for "hostname"
        if domain not in server:
            thisServer = server + "." + domain
        else:
            thisServer = server
        # print(server)

        # run local cmd on flask server to delete node from chef
        deleteNodeChefCmdString = '/bin/knife node delete {} -y -c {}'.format(thisServer, chefKnifeFileLocation)
        try:
            deleteNodeChefCmd = os.system(deleteNodeChefCmdString)
            deleteNodeExitCode = os.WEXITSTATUS(deleteNodeChefCmd)
        except Exception as e:
            error = "unable to run knife command: '{}' locally to delete node: '{}' from chef.".format(deleteNodeChefCmdString, server)
            print(error)
            print()
            general.showUserMessage(error)
            print("Exception:")
            print(e)
            general.showUserMessage("Exception:")
            general.showUserMessage(str(e))
            general.showUserMessage(".")
            deleteNodeExitCode = 1
        
        # run local cmd on flask server to delete client from chef
        deleteClientChefCmdString = '/bin/knife client delete {} -y -c {}'.format(thisServer, chefKnifeFileLocation)
        try:
            deleteClientChefCmd = os.system(deleteClientChefCmdString)
            deleteClientExitCode = os.WEXITSTATUS(deleteClientChefCmd)
        except Exception as e:
            error = "unable to run knife command: '{}' locally to delete client: '{}' from chef.".format(deleteClientChefCmdString, server)
            print(error)
            print()
            general.showUserMessage(error)
            print("Exception:")
            print(e)
            general.showUserMessage("Exception:")
            general.showUserMessage(str(e))
            general.showUserMessage(".")
            deleteClientExitCode = 1
        
        if deleteNodeExitCode == 0 and deleteClientExitCode == 0:
            liveMessage = "server: '{}' node and client successfully deleted from chef.".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            general.showUserMessage(".")
        else:
            liveMessage = "FAILED to delete server: '{}' from chef, please check what exception was raised above...".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            general.showUserMessage(".")


def verifyChefDecomm(server):
    chefDecommStatus = str()
    activeStatus = "Currently active"
    deactivatedStatus = "Deactivated"
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Chef Node Verify Decomm Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    liveMessage = "checking if server: '{}' was successfully removed from chef.".format(server)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    # server = server.lower()
    # remove "<domain>" from server name so that it'll match in the puppet query for "hostname"
    if domain not in server:
        thisServer = server + "." + domain
    else:
        thisServer = server
    # print(server)

    # run local cmd on flask server to verify that node was removed from from chef
    verifyNodeChefCmdString = '/bin/knife node list -c {} | /bin/grep -i {}'.format(chefKnifeFileLocation, thisServer)
    try:
        verifyNodeChefCmd = os.system(verifyNodeChefCmdString)
        verifyNodeExitCode = os.WEXITSTATUS(verifyNodeChefCmd)
    except Exception as e:
        error = "unable to run knife command: '{}' locally to verify node: '{}' status on chef.".format(verifyNodeChefCmdString, server)
        print(error)
        print()
        general.showUserMessage(error)
        print("Exception:")
        print(e)
        general.showUserMessage("Exception:")
        general.showUserMessage(str(e))
        general.showUserMessage(".")
        verifyNodeExitCode = 0
    
    # run local cmd on flask server to verify that client was removed from from chef
    verifyClientChefCmdString = '/bin/knife client list -c {} | /bin/grep -i {}'.format(chefKnifeFileLocation, thisServer)
    try:
        verifyClientChefCmd = os.system(verifyClientChefCmdString)
        verifyClientExitCode = os.WEXITSTATUS(verifyClientChefCmd)
    except Exception as e:
        error = "unable to run knife command: '{}' locally to verify client: '{}' status on chef.".format(verifyNodeChefCmdString, server)
        print(error)
        print()
        general.showUserMessage(error)
        print("Exception:")
        print(e)
        general.showUserMessage("Exception:")
        general.showUserMessage(str(e))
        general.showUserMessage(".")
        verifyClientExitCode = 0
    
    if verifyNodeExitCode != 0 and verifyClientExitCode != 0:
        chefDecommStatus = deactivatedStatus
        liveMessage = "server: '{}' was successfully removed from chef.".format(server)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        general.showUserMessage(".")
    else:
        chefDecommStatus = activeStatus
        liveMessage = "server: '{}' is still active on chef, delete method was UNSUCCESSFUL...".format(server)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        general.showUserMessage(".")

    return chefDecommStatus


def chefAPI():
    dotchef_knife_file_path = '/opt/flask/.chef/knife.rb'
    rootCAFile = '/etc/pki/ca-trust/source/anchors/frg-root-ca.crt'

    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    try:
        api = chef.autoconfigure(base_path = dotchef_knife_file_path)
        api.ssl_verify = rootCAFile
    except Exception as e:
        error = "Exception caught: '{}'".format(str(e))
        print(error)
        print()
        general.showUserMessage(error)
        session['flash_errors'] = error

    return api


def checkIfInChefAPI(serversList):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Check if Server in Chef Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    inChefServersList = list()
    notInChefServersList = list()

    liveMessage = "establishing ssl connection to chef API."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    try:
        chefAPI()
    except Exception as e:
        error = "Unable to esatblish ssl connection to chef API. Please contact the admins to investigate."
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")
        try:
            error = str(error) + " " + str(e)
            session['flash_errors'] = error
        except Exception as e:
            error = "Unable to esatblish ssl connection to chef API. Please contact the admins to investigate."
            session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")
    
    if error is None:
        liveMessage = "successfully established ssl connection to chef API."
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

    error = session.get('flash_errors')
    if error is None:

        for server in serversList:
            liveMessage = "checking if server: '{}' is in chef.".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            # server = server.lower()
            # append "<domain>" to server name if not there.
            if domain not in server:
                server = server + "." + domain

            try:
                node = chef.Node(server)
                if node.run_list:
                    inChefServersList.append(server)
                    liveMessage = "server: '{}' does exist on chef-server.".format(server)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)
                    general.showUserMessage(".")
                else:
                    notInChefServersList.append(server)
                    liveMessage = "server: '{}' does NOT exist on chef-server.".format(server)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)
                    general.showUserMessage(".")

            except Exception as e:
                notInChefServersList.append(server)
                error = "unable to connect to: 'chef-server' and determine if server: '{}' exists on 'chef-server'.".format(server)
                # session['flash_errors'] = error
                print(error)
                print()
                general.showUserMessage(error)
                print("Exception:")
                print(e)
                general.showUserMessage("Exception:")
                general.showUserMessage(str(e))
                general.showUserMessage(".")

    # remove duplicates from the list, if there are.
    if len(inChefServersList) > 0:
        inChefServersList = removeDuplicatesInList(inChefServersList)
        session['servers_found_in_chef_list'] = inChefServersList
    if len(notInChefServersList) > 0:
        notInChefServersList = removeDuplicatesInList(notInChefServersList)
        session['servers_not_found_in_chef_list'] = notInChefServersList


def removeDuplicatesInList(list):
    finalList = []
    for i in list:
        if i not in finalList:
            finalList.append(i)
    return finalList


def deleteChefNodesAPI(serversList):
    try:
        error = None
        session['flash_errors'] = error
    except:
        error = None

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Chef Node Delete Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    try:
        liveMessage = "establishing ssl connection to chef API."
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        try:
            chefAPI()
        except Exception as e:
            error = "Unable to esatblish ssl connection to chef API. Please contact the admins to investigate."
            print(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

            try:
                error = str(error) + " " + str(e)
                session['flash_errors'] = error
            except Exception as e:
                error = "Unable to esatblish ssl connection to chef API. Please contact the admins to investigate."
                session['flash_errors'] = error
                print(error)
                general.showUserMessage(error)
                print("Exception:")
                general.showUserMessage("Exception:")
                print(e)
                general.showUserMessage(str(e))
                general.showUserMessage(".")

        if error is None:
            liveMessage = "successfully established ssl connection to chef API."
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

        for server in serversList:
            if domain not in server:
                server = server + "." + domain

            liveMessage = "executing chef node delete function..."
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            try:
                node = chef.Node(server)
                node.delete()

                liveMessage = "success..."
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

            except Exception as e:
                error = "unable to connect to: 'chef-server' and delete server: '{}'.".format(server)
                # session['flash_errors'] = error
                print(error)
                print()
                general.showUserMessage(error)
                print("Exception:")
                print(e)
                general.showUserMessage("Exception:")
                general.showUserMessage(str(e))
                general.showUserMessage(".")

    except Exception as e:
        error = "Unable to esatblish ssl connection to chef API. Please contact the admins to investigate."
        # session['flash_errors'] = error
        print(error)
        print()
        general.showUserMessage(error)
        print("Exception:")
        print(e)
        general.showUserMessage("Exception:")
        general.showUserMessage(str(e))
        general.showUserMessage(".")


def verifyChefDecommAPI(server):
    chefDecommStatus = str()
    activeStatus = "Currently active"
    deactivatedStatus = "Deactivated"
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Chef Node Status Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    liveMessage = "establishing ssl connection to chef API."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    try:
        chefAPI()
    except Exception as e:
        error = "Unable to esatblish ssl connection to chef API. Please contact the admins to investigate."
        print(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")
        try:
            error = str(error) + " " + str(e)
            session['flash_errors'] = error
        except Exception as e:
            error = "Unable to esatblish ssl connection to chef API. Please contact the admins to investigate."
            session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

    if error is None:
        liveMessage = "successfully established ssl connection to chef API."
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

    error = session.get('flash_errors')
    if error is None:
        # server = server.lower()
        # append "<domain>" to server name if not there.
        if domain not in server:
            server = server + "." + domain

        liveMessage = "checking if server: '{}' is in chef.".format(server)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        try:
            verify_node = Node(server)

        except Exception as e:
            chefDecommStatus = activeStatus
            error = "unable to connect to: 'chef-server' and determine if server: '{}' exists on 'chef-server'.".format(server)
            session['flash_errors'] = error
            print(error)
            print()
            general.showUserMessage(error)
            print("Exception:")
            print(e)
            general.showUserMessage("Exception:")
            general.showUserMessage(str(e))
            general.showUserMessage(".")

        try:
            if verify_node.run_list:
                chefDecommStatus = activeStatus
            else:
                chefDecommStatus = deactivatedStatus

        except Exception as e:
            chefDecommStatus = activeStatus
            error = "unable to get 'run_list' of server: '{}' from 'chef-server'.".format(server)
            session['flash_errors'] = error
            print(error)
            print()
            general.showUserMessage(error)
            print("Exception:")
            print(e)
            general.showUserMessage("Exception:")
            general.showUserMessage(str(e))
            general.showUserMessage(".")

    return chefDecommStatus
