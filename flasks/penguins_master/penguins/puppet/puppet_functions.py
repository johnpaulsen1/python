from flask import session
import paramiko
from penguins.auth import domain, userDomain
from penguins.server import server_functions
from penguins.other_utils import general
from time import sleep

vmNamesList = list()
physicalNamesList = list()
zLinuxNamesList = list()
kvmNamesList = list()
cantFindServersList = list()

foundPhysicalsVisibility = str()
foundZLinuxVisibility = str()

virtualKeyWord = "vmware"
physicalKeyWord = "physical"
zLinuxKeyWord = "zlinux"
kvmKeyWord = "kvm"

jumpBox = "<jump server>"
kermit = "<puppet ca>"
puppetProxy = "<puppet proxy>"

stars = "*" * 70

def connectKermit(proxyHost, user, IDMPassword):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    if userDomain in user:
        # removes the "@<domain>" from the user variable, if there.
        user = user.replace(userDomain, "")

    # setup SSH client
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    except Exception as e:
        error = "Exception caught: '{}'".format(str(e))
        print(error)
        print()
        general.showUserMessage(error)
        session['flash_errors'] = error

    liveMessage = "setting proxy jump param for: '{}'".format(kermit)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    try:
        proxy = paramiko.ProxyCommand('/bin/ssh -o StrictHostKeyChecking=no '+ proxyHost +' nc '+ kermit +' 22')
        liveMessage = "success..."
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        general.showUserMessage(".")
    except Exception as e:
        error = "unable to set proxy connection from: '{}', to: '{}'. {}".format(proxyHost, kermit, str(e))
        session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

    liveMessage = "establishing connection to: '{}'".format(kermit)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    try:
        client.connect(kermit, 22, username=user, password=IDMPassword,
                        sock=proxy, timeout=10, auth_timeout=5, allow_agent=False,
                        look_for_keys=False)
        liveMessage = "success..."
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
    except Exception as e:
        error = "unable to establish connection to: '{}'. {}".format(kermit, str(e))
        session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

    return client


def checkIfInPuppet(serversList, user, IDMPassword):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Check if Server in Puppet Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    inPuppetServersList = list()
    notInPuppetServersList = list()
    baseCommand1st = "sudo puppet query facts --facts hostname '(\"hostname\" = \""
    baseCommand2nd = "\")'"

    liveMessage = "establishing ssh client to: '{}'".format(kermit)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    try:
        sshKermit = connectKermit(jumpBox, user, IDMPassword)
    except Exception as e:
        try:
            if error == None:
                error = str(e)
                session['flash_errors'] = error
            else:
                error = str(error) + " " + str(e)
                session['flash_errors'] = error
        except Exception as e:
            error = "It's likely that you are using an incorrect 'IDM' password. Please check and try again."
            session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

    error = session.get('flash_errors')
    if error is None:
        transport = sshKermit.get_transport()
        for server in serversList:
            liveMessage = "checking if server: '{}' is in puppetdb.".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            foundServer = False
            # server = server.lower()
            # remove "<domain>" from server name so that it'll match in the puppet query for "hostname"
            if domain in server:
                server = server.replace("<domain>","")
            # print(server)

            # have to open a new session for each exec_command
            try:
                ssh_session = transport.open_session()
                ssh_session.set_combine_stderr(True)
                ssh_session.get_pty()

                command = baseCommand1st + server + baseCommand2nd
                ssh_session.exec_command(command)
                stdin = ssh_session.makefile('wb', -1)
                stdout = ssh_session.makefile('rb', -1)
                # must parse password to sudo command
                if 'sudo' in command:
                    stdin.write(IDMPassword +'\n')
                stdin.flush()

                statusCommandOutputList = stdout.read().splitlines()
                # remove sudo password prompt from output list:
                if 'sudo' in command:
                    statusCommandOutputList = statusCommandOutputList[1:]

                for line in statusCommandOutputList:
                    puppetQueryResult = line.decode()
                    if server in puppetQueryResult:
                        # append domain name to server name
                        # if domain not in server:
                        #     server = server + "." + domain
                        inPuppetServersList.append(server)
                        liveMessage = "server: '{}' is in puppetdb.".format(server)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)
                        general.showUserMessage(".")

                        foundServer = True
                        break;

                # close ssh session after command has executed per server
                ssh_session.close()
            except Exception as e:
                error = "unable to connect to: '{}' and check virtual fact for server: '{}'.".format(kermit, server)
                # session['flash_errors'] = error
                print(error)
                print()
                general.showUserMessage(error)
                print("Exception:")
                print(e)
                general.showUserMessage("Exception:")
                general.showUserMessage(str(e))
                general.showUserMessage(".")

            if foundServer == False:
                notInPuppetServersList.append(server)
                liveMessage = "server: '{}' is NOT in puppetdb.".format(server)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
                general.showUserMessage(".")

    # remove duplicates from the list, if there are.
    if len(inPuppetServersList) > 0:
        inPuppetServersList = removeDuplicatesInList(inPuppetServersList)
        session['servers_found_in_puppet_list'] = inPuppetServersList
    if len(notInPuppetServersList) > 0:
        notInPuppetServersList = removeDuplicatesInList(notInPuppetServersList)
        session['servers_not_found_in_puppet_list'] = notInPuppetServersList


def removeDuplicatesInList(list):
    finalList = []
    for i in list:
        if i not in finalList:
            finalList.append(i)
    return finalList



def deactivatePuppetNode(serversList, user, IDMPassword):
    try:
        error = None
        session['flash_errors'] = error
    except:
        error = None

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Puppet Node Deactivation Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    try:
        liveMessage = "establishing ssh client to: '{}'".format(kermit)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        try:
            # establish connection to kermit
            sshKermit = connectKermit(jumpBox, user, IDMPassword)
        except Exception as e:
            try:
                if error == None:
                    error = str(e)
                    # session['flash_errors'] = error
                else:
                    error = str(error) + " " + str(e)
                    # session['flash_errors'] = error
            except Exception as e:
                error = "unable to determine error, please ask the admin to check."
                # session['flash_errors'] = error
                general.showUserMessage(error)
                print("Exception:")
                general.showUserMessage("Exception:")
                print(e)
                general.showUserMessage(str(e))
                general.showUserMessage(".")

        # setup pty session to enable sudo stuffs...
        transport = sshKermit.get_transport()

        for server in serversList:
            if domain not in server:
                server = server + "." + domain

            # have to open a new session for each exec_command
            ssh_session = transport.open_session()
            ssh_session.set_combine_stderr(True)
            ssh_session.get_pty()

            deactivateCommand = "sudo puppet node deactivate " + server

            liveMessage = "executing puppet node deactivate command..."
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            try:
                ssh_session.exec_command(deactivateCommand)

                liveMessage = "success..."
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                stdin = ssh_session.makefile('wb', -1)
                stdout = ssh_session.makefile('rb', -1)
                stdin.write(IDMPassword +'\n')
                stdin.flush()

                # remove password from output list
                statusCommandOutputList = stdout.read().splitlines()
                statusCommandOutputList = statusCommandOutputList[2:]
                print()
                liveMessage = "results:"
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
                general.showUserMessage(".")
                for line in statusCommandOutputList:
                    liveMessage = line.decode()
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                liveMessage = "successfully deactivated puppet node for server: '{}'.".format(server)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
                general.showUserMessage(".")

            except:
                liveMessage = "unable to execute puppet node deactivate command for server: '{}'.".format(server)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
                general.showUserMessage(".")

        ssh_session.close()
    except Exception as e:
        error = "unable to establish connection to: '{}' to deactivate puppet for server: '{}'.".format(kermit, server)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")


def statusPuppetNode(serversList, user, IDMPassword):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Puppet Node Status Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    try:
        liveMessage = "establishing ssh client to: '{}'".format(kermit)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        try:
            sshKermit = connectKermit(jumpBox, user, IDMPassword)
        except Exception as e:
            try:
                if error == None:
                    error = str(e)
                    # session['flash_errors'] = error
                else:
                    error = str(error) + " " + str(e)
                    # session['flash_errors'] = error
            except Exception as e:
                error = "unable to determine error, please ask the admin to check."
                # session['flash_errors'] = error
                print("Exception:")
                general.showUserMessage("Exception:")
                print(e)
                general.showUserMessage(str(e))
                general.showUserMessage(".")

        # set transport param used to open a new session.
        transport = sshKermit.get_transport()

        for server in serversList:
            if domain not in server:
                server = server + "." + domain

            statusCommand = "sudo puppet node status " + server

            # have to open a new session for each exec_command
            ssh_session = transport.open_session()
            ssh_session.set_combine_stderr(True)
            ssh_session.get_pty()

            liveMessage = "executing puppet node status check command for server '{}'".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            ssh_session.exec_command(statusCommand)

            liveMessage = "success..."
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            stdin = ssh_session.makefile('wb', -1)
            stdout = ssh_session.makefile('rb', -1)
            stdin.write(IDMPassword +'\n')
            stdin.flush()

            # remove password from output list
            statusCommandOutputList = stdout.read().splitlines()
            statusCommandOutputList = statusCommandOutputList[2:]

            print()
            liveMessage = "results:"
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            for line in statusCommandOutputList:
                liveMessage = line.decode()
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

            general.showUserMessage(".")
            ssh_session.close()
    except Exception as e:
        error = "unable to establish connection to: '{}' to check puppet status for server: '{}'.".format(kermit, server)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")


def connectPuppetProxy(proxyHost, user, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    if userDomain in user:
        # removes the "@<domain>" from the user variable, if there.
        user = user.replace(userDomain, "")

    # setup SSH client
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    liveMessage = "setting proxy jump param for '{}'".format(puppetProxy)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    try:
        proxy = paramiko.ProxyCommand('/bin/ssh -o StrictHostKeyChecking=no '+ proxyHost +' nc '+ puppetProxy +' 22')
        liveMessage = "success..."
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
    except Exception as e:
        error = "unable to set proxy connection from: '{}', to: '{}'.".format(proxyHost, puppetProxy)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

    liveMessage = "establishing connection to: '{}'".format(puppetProxy)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    try:
        client.connect(puppetProxy, 22, username=user,  password=password, sock=proxy)
        liveMessage = "success..."
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        general.showUserMessage(".")
    except paramiko.ssh_exception.AuthenticationException as e:
        error = "unable to establish connection to: '{}'.".format(puppetProxy)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

    return client


def cleanPuppetCerts(serversList, user, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Puppet Node Cert Revoke Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    try:
        sshPuppetProxy = connectPuppetProxy(jumpBox, user, password)

        # set transport param used to open a new session.
        transport = sshPuppetProxy.get_transport()

        for server in serversList:
            if domain not in server:
                server = server + "." + domain

            revokeCertCommand = "sudo puppet cert clean " + server

            # have to open a new session for each exec_command
            ssh_session = transport.open_session()
            ssh_session.set_combine_stderr(True)
            ssh_session.get_pty()

            liveMessage = "executing cert revoke command for server: '{}'".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            ssh_session.exec_command(revokeCertCommand)

            liveMessage = "success..."
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            stdin = ssh_session.makefile('wb', -1)
            stdout = ssh_session.makefile('rb', -1)
            stdin.write(password +'\n')
            stdin.flush()

            # remove password from output list
            revokeCertCommandOutputList = stdout.read().splitlines()
            revokeCertCommandOutputList = revokeCertCommandOutputList[2:]

            print()
            liveMessage = "results:"
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            for line in revokeCertCommandOutputList:
                liveMessage = line.decode()
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

            general.showUserMessage(".")
            ssh_session.close()

    except Exception as e:
        error = "unable to establish connection to: '{}' to revoke puppet cert for server: '{}'".format(puppetProxy, server)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")


def statusPuppetCerts(serversList, user, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Puppet Node Cert Status Check Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    try:
        sshPuppetProxy = connectPuppetProxy(jumpBox, user, password)

        # set transport param used to open a new session.
        transport = sshPuppetProxy.get_transport()

        for server in serversList:
            if domain not in server:
                server = server + "." + domain

            certStatusCommand = "sudo puppet cert list " + server

            # have to open a new session for each exec_command
            ssh_session = transport.open_session()
            ssh_session.set_combine_stderr(True)
            ssh_session.get_pty()

            liveMessage = "executing cert status check command for server: '{}'".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            ssh_session.exec_command(certStatusCommand)

            liveMessage = "success..."
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            stdin = ssh_session.makefile('wb', -1)
            stdout = ssh_session.makefile('rb', -1)
            stdin.write(password +'\n')
            stdin.flush()

            # remove password from output list:
            certStatusCommandOutputList = stdout.read().splitlines()
            certStatusCommandOutputList = certStatusCommandOutputList[2:]
            print()
            liveMessage = "results:"
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            for line in certStatusCommandOutputList:
                liveMessage = line.decode()
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

            general.showUserMessage(".")
            ssh_session.close()

    except Exception as e:
        error = "unable to establish connection to: '{}' to check puppet cert status for server: '{}'".format(puppetProxy, server)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

def puppetDecommActions(serversList, user, adPass, idmPass, coNumber):
    # method to kill puppet
    server_functions.killPuppet(jumpBox, serversList, user, adPass)
    print("*****************************")
    print()

    # method to remove puppet package
    # server_functions.removePuppetPackage(jumpBox, serversList, user, adPass)
    # print("*****************************")
    # print()

    # method to remove puppet package
    server_functions.disablePuppet(jumpBox, serversList, user, adPass, coNumber)
    print("*****************************")
    print()

    # method to deactivate puppet node
    deactivatePuppetNode(serversList, user, idmPass)
    print("*****************************")
    print()

    liveMessage = "."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "sleeping for 10 seconds, to allow puppetbd to register the deactivate command/s."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    sleep(10)

    # method to check puppet nodes status on kermit
    statusPuppetNode(serversList, user, idmPass)
    print("*****************************")
    print()

    # method to clean puppet certs on puppet proxy
    cleanPuppetCerts(serversList, user, adPass)
    print("*****************************")
    print()

    # method to check puppet cert for nodes on puppet proxy
    statusPuppetCerts(serversList, user, adPass)
    print("*****************************")
    print()

def verifyPuppetDecomm(server, user, idmPass):
    puppetDecommStatus = str()
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

    liveMessage = "Puppet Node Status Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    try:
        liveMessage = "establishing ssh client to: '{}'".format(kermit)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        try:
            sshKermit = connectKermit(jumpBox, user, idmPass)
        except Exception as e:
            try:
                if error == None:
                    error = str(e)
                    # session['flash_errors'] = error
                else:
                    error = str(error) + " " + str(e)
                    # session['flash_errors'] = error
            except Exception as e:
                error = "unable to determine error, please ask the admin to check."
                # session['flash_errors'] = error
                print("Exception:")
                general.showUserMessage("Exception:")
                print(e)
                general.showUserMessage(str(e))
                general.showUserMessage(".")

        # set transport param used to open a new session.
        transport = sshKermit.get_transport()

        if domain not in server:
            server = server + "." + domain

        statusCommand = "sudo puppet node status " + server

        # have to open a new session for each exec_command
        ssh_session = transport.open_session()
        ssh_session.set_combine_stderr(True)
        ssh_session.get_pty()

        liveMessage = "executing puppet node status check command for server: '{}'".format(server)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        ssh_session.exec_command(statusCommand)

        liveMessage = "success..."
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        stdin = ssh_session.makefile('wb', -1)
        stdout = ssh_session.makefile('rb', -1)
        stdin.write(idmPass +'\n')
        stdin.flush()

        # remove password from output list
        statusCommandOutputList = stdout.read().splitlines()
        statusCommandOutputList = statusCommandOutputList[2:]
        foundStatus = False
        foundStatusStr = str()

        for line in statusCommandOutputList:
            if deactivatedStatus in str(line):
                foundStatus = True
                puppetDecommStatus = deactivatedStatus
                break;
            elif activeStatus in str(line):
                foundStatus = True
                puppetDecommStatus = activeStatus
                break;

        if foundStatus == False:
            puppetDecommStatus = activeStatus

        general.showUserMessage(".")
        ssh_session.close()

    except Exception as e:
        error = "unable to establish connection to: '{}' to check puppet status for server: '{}'.".format(kermit, server)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

    return puppetDecommStatus
