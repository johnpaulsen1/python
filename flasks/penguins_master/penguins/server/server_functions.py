from flask import session
import paramiko
from penguins.auth import domain, userDomain
from penguins.other_utils import general

stars = "*" * 70

def getSSHConnection(proxyHost, hostName, user, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error
    if domain in user:
        # removes the "@<domain>" from the user variable, if there.
        user = user.replace(userDomain, "")

    # setup SSH client
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # message to be displayed to user on live messages page
    liveMessage = "setting proxy jump param for: '{}'".format(hostName)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    try:
        proxy = paramiko.ProxyCommand('/bin/ssh -o StrictHostKeyChecking=no '+ proxyHost +' nc '+ hostName +' 22')
        # message to be displayed to user on live messages page
        liveMessage = "success..."
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
    except Exception as e:
        # message to be displayed to user on live messages page
        error = "unable to set proxy connection from: '{}', to: '{}'.".format(proxyHost, hostName)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

    # message to be displayed to user on live messages page
    liveMessage = "attempting to establish connection to server: '{}'.".format(hostName)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    try:
        client.connect(hostName, 22, username=user,  password=password,
                        sock=proxy, timeout=10, auth_timeout=5, allow_agent=False,
                        look_for_keys=False, banner_timeout=100)
        # message to be displayed to user on live messages page
        liveMessage = "success..."
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        general.showUserMessage(".")
        return client
    except paramiko.ssh_exception.SSHException as e:
        # message to be displayed to user on live messages page
        error = "ssh exception caught while connecting to: '{}', via proxy: '{}'.".format(hostName, proxyHost)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

        client = None
        return client

    except paramiko.ssh_exception.AuthenticationException as e:
        # message to be displayed to user on live messages page
        error = "unable to establish connection to: '{}'.".format(hostName)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

        client = None
        return client

    except Exception as e:
        # message to be displayed to user on live messages page
        error = "unable to establish connection to: '{}'.".format(hostName)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

        client = None
        return client


def runCmdOnClient(ssh_client, command, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error
    cmdOutputList = list()
    try:
        # setup pty session to enable sudo stuffs...
        transport = ssh_client.get_transport()

        ssh_session = transport.open_session()
        ssh_session.set_combine_stderr(True)
        ssh_session.get_pty()

        ssh_session.exec_command(command)
        stdin = ssh_session.makefile('wb', -1)
        stdout = ssh_session.makefile('rb', -1)
        # must parse password to sudo command
        if 'sudo' in command:
            stdin.write(password +'\n')

        stdin.flush()

        cmdOutput = stdout.read().splitlines()
        # remove sudo password prompt from output list:
        if 'sudo' in command:
            cmdOutput = cmdOutput[2:]

        for line in cmdOutput:
            outputLine = line.decode()
            if len(outputLine) > 0:
                cmdOutputList.append(outputLine)

        if len(cmdOutputList) == 1:
            return cmdOutput[0].decode()
        else:
            return cmdOutputList

    except Exception as e:
        # message to be displayed to user on live messages page
        error = "unable to connect to and run requested commands on server: '{}'.".format(ssh_client)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")


def checkAbleToSshToServer(serverNamesList, proxy, user, passwd):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error
    sshSuccessServersList = list()
    unableToSshSuccessServersList = list()

    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Check if able to ssh to server/s method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    for server in serverNamesList:
        ableToSsh = False
        commandOutput = None
        try:
            ssh_client = getSSHConnection(proxy, server, user, passwd)
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' via proxy: '{}'.".format(server, proxy)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

            ssh_client = None

        if ssh_client:
            sshSuccessServersList.append(server)
            ssh_client.close()
        else:
            unableToSshSuccessServersList.append(server)

    session['list_of_servers_able_to_ssh'] = sshSuccessServersList
    session['list_of_servers_unable_to_ssh'] = unableToSshSuccessServersList


def checkPhysicals(physicalNamesList, proxy, user, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Check Physical servers method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    listOfPhysicalInfoLists = list()

    for physicalServer in physicalNamesList:
        # print("getting ssh connection for: ", physicalServer)
        try:
            ssh_client = getSSHConnection(proxy, physicalServer, user, password)
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' via proxy: '{}'.".format(physicalServer, proxy)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

            ssh_client = None

        multiPhysicalsInfoList = list()
        commandList = list()
        multiPhysicalsInfoList.append(physicalServer)

        # commands to run on physical servers
        IPAdressCmd = "/sbin/ip a | grep -w inet | grep -v '127.0.0.1' | awk '{print $2}'"
        commandList.append(IPAdressCmd)
        SerialNumCmd = "sudo /usr/sbin/dmidecode -s system-serial-number"
        commandList.append(SerialNumCmd)
        upTimeCmd = "/usr/bin/uptime | sed 's/^ //g' | awk '{print $1, $2, $3, $4, $5}'"
        commandList.append(upTimeCmd)
        IMMCmd = "sudo /usr/bin/ipmitool lan print | grep -w 'IP Address' | grep -v 'IP Address Source' | cut -d ':' -f2 | sed 's/^ //g'"
        commandList.append(IMMCmd)
        OSCmd = "/usr/bin/lsb_release -a | egrep 'Distributor ID:|Release:' | cut -d ':' -f2 | awk '{print $1}' | tr '\n' ' '"
        commandList.append(OSCmd)
        numCPUsCmd = "/bin/grep -c ^processor /proc/cpuinfo"
        commandList.append(numCPUsCmd)
        numMemCmd = "/usr/bin/free -h | grep 'Mem:' | awk '{print $2}'"
        commandList.append(numMemCmd)

        # must open a new ssh session per command
        if ssh_client:
            for command in commandList:
                try:
                    commandOutput = runCmdOnClient(ssh_client, command, password)
                    multiPhysicalsInfoList.append(commandOutput)
                except Exception as e:
                    # message to be displayed to user on live messages page
                    error = "unable to connect to and run requested commands on server: '{}'.".format(physicalServer)
                    # session['flash_errors'] = error
                    print(error)
                    general.showUserMessage(error)
                    print("Exception:")
                    general.showUserMessage("Exception:")
                    print(e)
                    general.showUserMessage(str(e))
                    general.showUserMessage(".")

        elif ssh_client == None:
            for command in commandList:
                commandOutput = "Can't connect to server"
                multiPhysicalsInfoList.append(commandOutput)
        else:
            pass


        # print(multiPhysicalsInfoList)
        try:
            if ssh_client:
                ssh_client.close()
        except:
            pass

        listOfPhysicalInfoLists.append(multiPhysicalsInfoList)
        session['list_of_physical_info_lists'] = listOfPhysicalInfoLists


def checkZLinux(zLinuxNamesList, proxy, user, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error
    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Check zLinux servers method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    listOfZLinuxInfoLists = list()

    for zLinuxServer in zLinuxNamesList:
        # print("getting ssh connection for: ", physicalServer)
        try:
            ssh_client = getSSHConnection(proxy, zLinuxServer, user, password)
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' via proxy: '{}'.".format(zLinuxServer, proxy)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

            ssh_client = None

        multiZLinuxInfoList = list()
        commandList = list()
        multiZLinuxInfoList.append(zLinuxServer)

        # commands to run on physical servers
        IPAdressCmd = "/sbin/ip a | grep -w inet | grep -v '127.0.0.1' | awk '{print $2}'"
        commandList.append(IPAdressCmd)
        # SerialNumCmd = "sudo /usr/sbin/dmidecode -s system-serial-number"
        # commandList.append(SerialNumCmd)
        upTimeCmd = "/usr/bin/uptime | sed 's/^ //g' | awk '{print $1, $2, $3, $4, $5}'"
        commandList.append(upTimeCmd)
        OSCmd = "/usr/bin/lsb_release -a | egrep 'Distributor ID:|Release:' | cut -d ':' -f2 | awk '{print $1}' | tr '\n' ' '"
        commandList.append(OSCmd)
        numCPUsCmd = "/bin/grep -c ^processor /proc/cpuinfo"
        commandList.append(numCPUsCmd)
        numMemCmd = "/usr/bin/free -h | grep 'Mem:' | awk '{print $2}'"
        commandList.append(numMemCmd)

        if ssh_client:
            # must open a new ssh session per command
            for command in commandList:
                try:
                    commandOutput = runCmdOnClient(ssh_client, command, password)
                    multiZLinuxInfoList.append(commandOutput)
                except Exception as e:
                    # message to be displayed to user on live messages page
                    error = "unable to connect to and run requested commands on server: '{}'.".format(zLinuxServer)
                    # session['flash_errors'] = error
                    print(error)
                    general.showUserMessage(error)
                    print("Exception:")
                    general.showUserMessage("Exception:")
                    print(e)
                    general.showUserMessage(str(e))
                    general.showUserMessage(".")

        elif ssh_client == None:
            for command in commandList:
                commandOutput = "Can't connect to server"
                multiZLinuxInfoList.append(commandOutput)
        else:
            pass

        try:
            if ssh_client:
                ssh_client.close()
        except:
            pass
        # print(multiZLinuxInfoList)

        listOfZLinuxInfoLists.append(multiZLinuxInfoList)
        session['list_of_zlinux_info_lists'] = listOfZLinuxInfoLists


def checkKVM(kvmNamesList, proxy, user, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error
    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Check KVM servers method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    listOfZLinuxInfoLists = list()
    listOfKVMInfoLists = list()

    for kvmServer in kvmNamesList:
        # print("getting ssh connection for: ", physicalServer)
        try:
            ssh_client = getSSHConnection(proxy, kvmServer, user, password)
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' via proxy: '{}'.".format(kvmServer, proxy)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")
            ssh_client = None

        multiKVMInfoList = list()
        commandList = list()
        multiKVMInfoList.append(kvmServer)

        # commands to run on physical servers
        IPAdressCmd = "/sbin/ip a | grep -w inet | grep -v '127.0.0.1' | awk '{print $2}'"
        commandList.append(IPAdressCmd)
        # SerialNumCmd = "sudo /usr/sbin/dmidecode -s system-serial-number"
        # commandList.append(SerialNumCmd)
        upTimeCmd = "/usr/bin/uptime | sed 's/^ //g' | awk '{print $1, $2, $3, $4, $5}'"
        commandList.append(upTimeCmd)
        OSCmd = "/usr/bin/lsb_release -a | egrep 'Distributor ID:|Release:' | cut -d ':' -f2 | awk '{print $1}' | tr '\n' ' '"
        commandList.append(OSCmd)
        numCPUsCmd = "/bin/grep -c ^processor /proc/cpuinfo"
        commandList.append(numCPUsCmd)
        numMemCmd = "/usr/bin/free -h | grep 'Mem:' | awk '{print $2}'"
        commandList.append(numMemCmd)

        if ssh_client:
            # must open a new ssh session per command
            for command in commandList:
                try:
                    commandOutput = runCmdOnClient(ssh_client, command, password)
                    multiKVMInfoList.append(commandOutput)
                except Exception as e:
                    # message to be displayed to user on live messages page
                    error = "unable to connect to and run requested commands on server: '{}'.".format(kvmServer)
                    # session['flash_errors'] = error
                    print(error)
                    general.showUserMessage(error)
                    print("Exception:")
                    general.showUserMessage("Exception:")
                    print(e)
                    general.showUserMessage(str(e))
                    general.showUserMessage(".")

        elif ssh_client == None:
            for command in commandList:
                commandOutput = "Can't connect to server"
                multiKVMInfoList.append(commandOutput)
        else:
            pass

        try:
            if ssh_client:
                ssh_client.close()
        except:
            pass
        # print(multiZLinuxInfoList)

        listOfKVMInfoLists.append(multiKVMInfoList)
        session['list_of_kvm_info_lists'] = listOfKVMInfoLists

def powerDownPhysicals(proxy, serversList, user, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Power Down Physical Server/s Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    listOfZLinuxInfoLists = list()
    listOfKVMInfoLists = list()

    for server in serversList:
        try:
            ssh_client = getSSHConnection(proxy, server, user, password)
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' via proxy: '{}'.".format(server, proxy)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

        powerDownCmd = "sudo /sbin/shutdown now"

        liveMessage = "attempting to power down '{}' NOW".format(server)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        try:
            runCmdOnClient(ssh_client, powerDownCmd, password)
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to connect to and run requested commands on server: '{}'.".format(server)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

        if ssh_client:
            ssh_client.close()

def killPuppet(proxy, serversList, user, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Kill puppet if running on Server/s Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    listOfZLinuxInfoLists = list()
    listOfKVMInfoLists = list()

    for server in serversList:
        try:
            ssh_client = getSSHConnection(proxy, server, user, password)
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' via proxy: '{}'.".format(server, proxy)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

        if ssh_client:
            killPuppetCmd = "sudo pkill -9 -f puppet"

            # message to be displayed to user on live messages page
            liveMessage = "attempting to kill puppet on server: '{}' NOW...".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            general.showUserMessage(".")

            listOfZLinuxInfoLists = list()
            listOfKVMInfoLists = list()
            try:
                runCmdOnClient(ssh_client, killPuppetCmd, password)
            except Exception as e:
                # message to be displayed to user on live messages page
                error = "unable to connect to and run requested commands on server: '{}'.".format(server)
                # session['flash_errors'] = error
                print(error)
                general.showUserMessage(error)
                print("Exception:")
                general.showUserMessage("Exception:")
                print(e)
                general.showUserMessage(str(e))
                general.showUserMessage(".")

        if ssh_client:
            ssh_client.close()


def removePuppetPackage(proxy, serversList, user, password):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Remove puppet package from Server/s Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    for server in serversList:
        try:
            ssh_client = getSSHConnection(proxy, server, user, password)
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' via proxy: '{}'.".format(server, proxy)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

        removePuppetCmd = "sudo yum remove `rpm -qa | grep -i puppet` -y"

        # message to be displayed to user on live messages page
        liveMessage = "attempting to remove puppet on server: '{}' NOW...".format(server)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        general.showUserMessage(".")
        try:
            runCmdOnClient(ssh_client, removePuppetCmd, password)
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to connect to and run requested commands on server: '{}'.".format(server)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")

        if ssh_client:
            ssh_client.close()


def disablePuppet(proxy, serversList, user, password, coNumber):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Disable Puppet Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    cronFileName = "/var/spool/cron/root"
    rcDotLocalFileName = "/etc/rc.local"

    for server in serversList:

        try:
            ssh_client = getSSHConnection(proxy, server, user, password)
        except Exception as e:
            # message to be displayed to user on live messages page
            error = "unable to establish connection to: '{}' via proxy: '{}'.".format(server, proxy)
            # session['flash_errors'] = error
            print(error)
            general.showUserMessage(error)
            print("Exception:")
            general.showUserMessage("Exception:")
            print(e)
            general.showUserMessage(str(e))
            general.showUserMessage(".")



        if ssh_client:
            # check if files to update exist.

            listCronFileCmd = "sudo ls " + cronFileName

            # message to be displayed to user on live messages page
            liveMessage = "checking if root cron file exists on server: '{}' NOW...".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            try:
                listCronFileCmdOutputList = runCmdOnClient(ssh_client, listCronFileCmd, password)
            except Exception as e:
                listCronFileCmdOutputList = None
                # message to be displayed to user on live messages page
                error = "unable to connect to and run requested commands on server: '{}'.".format(server)
                # session['flash_errors'] = error
                print(error)
                general.showUserMessage(error)
                print("Exception:")
                general.showUserMessage("Exception:")
                print(e)
                general.showUserMessage(str(e))
                general.showUserMessage(".")

            if cronFileName in listCronFileCmdOutputList:
                cronFileThere = True
            else:
                cronFileThere = False


            listRCDotLocalFileCmd = "sudo ls " + rcDotLocalFileName

            # message to be displayed to user on live messages page
            liveMessage = "checking if rc.local file exists on server: '{}' NOW...".format(server)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            try:
                listRCDotLocalFileCmdOutputList = runCmdOnClient(ssh_client, listRCDotLocalFileCmd, password)
            except Exception as e:
                listRCDotLocalFileCmdOutputList = None
                # message to be displayed to user on live messages page
                error = "unable to connect to and run requested commands on server: '{}'.".format(server)
                # session['flash_errors'] = error
                print(error)
                general.showUserMessage(error)
                print("Exception:")
                general.showUserMessage("Exception:")
                print(e)
                general.showUserMessage(str(e))
                general.showUserMessage(".")

            if rcDotLocalFileName in listRCDotLocalFileCmdOutputList:
                rcDotLocalFileThere = True
            else:
                rcDotLocalFileThere = False


            if cronFileThere:
                updateCronFileCmd = "sudo sed -i -e '/puppet_agent/d' -e '/Puppet Name: puppet/d' -e '$a# /usr/local/bin/puppet_agent.sh removed by user: " + user + " for decomm CO: " + coNumber +"' " + cronFileName
                try:
                    # message to be displayed to user on live messages page
                    liveMessage = "hashing out puppet from root cron file on server: '{}' NOW...".format(server)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)
                    general.showUserMessage(".")
                    runCmdOnClient(ssh_client, updateCronFileCmd, password)
                except Exception as e:
                    # message to be displayed to user on live messages page
                    error = "unable to connect to and run requested commands on server: '{}'.".format(server)
                    # session['flash_errors'] = error
                    print(error)
                    general.showUserMessage(error)
                    print("Exception:")
                    general.showUserMessage("Exception:")
                    print(e)
                    general.showUserMessage(str(e))
                    general.showUserMessage(".")


            if rcDotLocalFileThere:
                updateRCDotLocalFileCmd = "sudo sed -i -e '$a# /usr/bin/puppet agent removed by user: " + user + " for decomm CO: " + coNumber + "' -e '/puppet agent/d' -e '/puppet_agent.sh/d' " + rcDotLocalFileName
                try:
                    # message to be displayed to user on live messages page
                    liveMessage = "hashing out puppet from rc.local file on server: '{}' NOW...".format(server)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)
                    general.showUserMessage(".")
                    runCmdOnClient(ssh_client, updateRCDotLocalFileCmd, password)
                except Exception as e:
                    # message to be displayed to user on live messages page
                    error = "unable to connect to and run requested commands on server: '{}'.".format(server)
                    # session['flash_errors'] = error
                    print(error)
                    general.showUserMessage(error)
                    print("Exception:")
                    general.showUserMessage("Exception:")
                    print(e)
                    general.showUserMessage(str(e))
                    general.showUserMessage(".")


def verifyPhysicalDecomm(server, user, password, proxy):
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error

    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Check if able to ssh to server/s method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    activeStatus = "Currently active"
    deactivatedStatus = "Deactivated"
    physicalDecommStatus = str()

    try:
        ssh_client = getSSHConnection(proxy, server, user, password)
    except Exception as e:
        # message to be displayed to user on live messages page
        error = "unable to establish connection to: '{}' via proxy: '{}'.".format(server, proxy)
        # session['flash_errors'] = error
        print(error)
        general.showUserMessage(error)
        print("Exception:")
        general.showUserMessage("Exception:")
        print(e)
        general.showUserMessage(str(e))
        general.showUserMessage(".")

        ssh_client = None

    if ssh_client:
        physicalDecommStatus = activeStatus
        ssh_client.close()
    else:
        physicalDecommStatus = deactivatedStatus

    return physicalDecommStatus
