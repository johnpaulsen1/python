import requests
from flask import session
from penguins.auth import domain, userDomain
from penguins.other_utils import general

satelliteURL = "https://<url here>"
satelliteAPI = satelliteURL + "/api/v2"
katelloAPI = satelliteURL + "katello/api"
postHeaders = {'content-type': 'application/json'}

stars = "*" * 70

def statusServerSatellite(serversList, user, password):
    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Server Status Check on Satellite Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)


    if userDomain in user:
        # removes the "@<domain>" from the user variable, if there.
        user = user.replace(userDomain, "")

    for server in serversList:
        if domain not in server:
            server = server + "." + domain

        host_url = satelliteAPI + "/hosts/" + server
        host_dict = {}

        # req = requests.get(host_url, auth=(user, password), verify=False)
        try:
            getReq = requests.get(host_url, auth=(user, password), verify=False)
            host_data = getReq.json()
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' to check server status for server: '{}'.".format(satelliteAPI, server)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))

        try:
            created_date = host_data['created_at']
        except:
            created_date = "None"

        try:
            os_name = host_data['operatingsystem_name']
        except:
            os_name = "None"

        try:
            arch_type = host_data['subscription_facet_attributes']['host_type']
        except:
            arch_type = "None"

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

        host_dict['hostname'] = server
        host_dict['date_added'] = created_date
        host_dict['os_name'] = os_name
        host_dict['arch_type'] = arch_type
        host_dict['capsule'] = capsule
        host_dict['subscription_status'] = subscription_status
        host_dict['esx_host'] = esx_host

        # message to be displayed to user on live messages page
        liveMessage = "Results:"
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        for key, val in host_dict.items():
            # message to be displayed to user on live messages page
            liveMessage = "'{}': '{}'".format(key, val)
            print(liveMessage)
            general.showUserMessage(liveMessage)
        print()
        general.showUserMessage(".")


def deleteServerSatellite(serversList, user, password):
    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Delete Server on Satellite Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    if domain in user:
        # removes the "@<domain>" from the user variable, if there.
        user = user.replace(userDomain, "")

    for server in serversList:
        if domain not in server:
            server = server + "." + domain

        host_url = satelliteAPI + "/hosts/" + server

        try:
            delReq = requests.delete(host_url, auth=(user, password), verify=False)
            delReqJsonResult = delReq.json()
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' to delete server: '{}'.".format(satelliteAPI, server)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))

        try:
            if delReqJsonResult:
                # message to be displayed to user on live messages page
                liveMessage = "Results:"
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                liveMessage = delReqJsonResult
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
        except:
            pass

def checkIfServerInSatellite(serversList, user, password):
    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Check if Server in Satellite Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    inSatelliteServersList = list()
    notInSatelliteServersList = list()

    if domain in user:
        # removes the "@<domain>" from the user variable, if there.
        user = user.replace(userDomain, "")

    for server in serversList:
        if domain not in server:
            server = server + "." + domain

        host_url = satelliteAPI + "/hosts/" + server

        try:
            getReq = requests.get(host_url, auth=(user, password), verify=False)
            host_data = getReq.json()
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' to check server status for server: '{}'.".format(satelliteAPI, server)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))

        try:
            if host_data['created_at']:
                if domain in server:
                    server = server.replace("." + domain, "")
                inSatelliteServersList.append(server)

                # message to be displayed to user on live messages page
                liveMessage = "Server: '{}' in satellite.".format(server)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
            else:
                notInSatelliteServersList.append(server)
                liveMessage = "Server: '{}' NOT in satellite.".format(server)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
        except:
            if server not in notInSatelliteServersList:
                notInSatelliteServersList.append(server)
            liveMessage = "Server: '{}' NOT in satellite.".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

        general.showUserMessage(".")

    session['servers_in_satellite_list'] = inSatelliteServersList
    session['servers_not_in_satellite_list'] = notInSatelliteServersList


def satelliteDecommActions(serversList, user, adPass):
    # method to check servers status on satellite
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "check satellite status BEFORE delete"
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    statusServerSatellite(serversList, user, adPass)

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    # method to delete servers on satellite
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "delete server from satellite"
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    deleteServerSatellite(serversList, user, adPass)

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    # method to check servers status on satellite
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "check satellite status AFTER delete"
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    statusServerSatellite(serversList, user, adPass)

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")


def verifySatelliteDecomm(server, user, password):
    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Verfiy that Server has been Removed out of Satellite Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    activeStatus = "Currently active"
    deactivatedStatus = "Deactivated"
    satelliteDecommStatus = str()

    if domain in user:
        # removes the "@<domain>" from the user variable, if there.
        user = user.replace(userDomain, "")

    if domain not in server:
        server = server + "." + domain

    host_url = satelliteAPI + "/hosts/" + server

    try:
        getReq = requests.get(host_url, auth=(user, password), verify=False)
        host_data = getReq.json()
        checkHostNotInSatellite = host_data['error']
    except Exception as e:
        # message to be displayed to user on live messages page
        error = "unable to establish connection to: '{}' to check server status for server: '{}'.".format(satelliteAPI, server)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))

        satelliteDecommStatus = activeStatus


    if checkHostNotInSatellite:
        satelliteDecommStatus = deactivatedStatus
    else:
        satelliteDecommStatus = activeStatus

    return satelliteDecommStatus
