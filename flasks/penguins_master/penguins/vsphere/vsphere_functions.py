from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from flask import session
from os import path
from time import sleep
from penguins.auth import domain
from penguins.other_utils import general

# declare variables
vmVsphereInstancesList = list()
listOfVMInfoLists = list()
vmNICNamesList = list()
vmNICStatesList = list()
foundVCsList = list()
dcObjsList = list()
siList = list()
vcsList = list()
knownVsphereVCs = list()
foundVMsVisibility = str()
cantFindVMsVCInfoVisibility = str()
cantFindServersVisibility = str()

knownVsphereVCsFile = "vsphere_vcenters"

stars = "*" * 70
lines = "-" * 70

try:
    error = None
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "..", "./static/", knownVsphereVCsFile))
    openKnownVsphereVCsFile = open(filepath, "r")
    knownVsphereVCs = openKnownVsphereVCsFile.read().splitlines()
except:
    error = "unable to read file: " + filepath
    # session['flash_errors'] = error
    knownVsphereVCs = list()
print(error)


# vcsList = [labVC, nonProdVC, ProdVC1, ProdVC2, splunkVC]
# vcsList = [nonProdVC, ProdVC1, ProdVC2, splunkVC]
# vcsList = [ProdVC2, splunkVC, nonProdVC, ProdVC1]
vcsList = knownVsphereVCs
numVCs = len(vcsList)
maxLoops = 10

displayVMListStatics = ['VM Name:', 'VC:', 'Parent Folder', 'VM UUID:',
'Power State:', 'Running State:', 'VM IP:', 'VM MAC:', 'VM OS:', 'Num CPU\'s:',
'Memory (MB):', 'VM NIC Device/s:', 'VM NIC/s State:']

baseDeleteFolder = "0_Monthly_Deletions"
vmNICState = "disconnect"

# Create service instance of VCenter/s
def ServiceInstance(vc, user, password):
    si = SmartConnect(host=vc, user=user, pwd=password)
    return si


def getAllVMInstances(user, password):
    vimtype = [vim.VirtualMachine]
    vmObjsList = list()

    for vc in vcsList:
        # message to be displayed to user on live messages page
        liveMessage = "{}".format(stars)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "getting all VM's in VC: '{}'".format(vc)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        vmObj = None
        si = None

        try:
            si = ServiceInstance(vc, user, password)
            content = si.content
            container = content.viewManager.CreateContainerView(
                content.rootFolder, vimtype, True)

            for vmObj in container.view:
                vmObjsList.append(vmObj)

        except:
            si = None

    return vmObjsList


def checkIfServerInVsphere(serversList, user, password):
    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Check if Server in Vsphere Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    inVsphereServersList = list()
    notInVsphereServersList = list()

    print()

    for server in serversList:
        liveMessage = "{}".format(stars)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        # set to lowercase, as VM's are lower case in most cases in our vcenters
        server = server.lower()

        # message to be displayed to user on live messages page
        liveMessage = "finding vc for vm: '{}'".format(server)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        if domain in server:
            server = server.replace("." + domain,"")

        for vc in vcsList:
            liveMessage = "checking VC: '{}'".format(vc)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            vmObj = None

            try:
                si = ServiceInstance(vc, user, password)
                content = si.content
            except:
                si = None
            try:
                vmObj = getVMInstanceByName(si, server)
                if vmObj:
                    foundVM = True
                    # message to be displayed to user on live messages page
                    liveMessage = "VM: {} resides in VC: {}".format(server, vc)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    vmName = vmObj.config.name
                    inVsphereServersList.append(vmName)
                    break;
            except:
                pass

        if foundVM == False:
            notInVsphereServersList.append(server)

    session['servers_in_vsphere_list'] = inVsphereServersList
    session['servers_not_in_vsphere_list'] = notInVsphereServersList



def getVsphereObj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def getVMInstanceByName(si, name):
    return getVsphereObj(si.RetrieveContent(), [vim.VirtualMachine], name)


def getVMInstanceByMAC(vmObjsList, macList):
    vmNICPrefixLabel = "Network adapter "
    cantFindVMsList = list()
    cantFindVMsVCInfoVisibility = "visibility_off"
    foundVmObjsList = list()
    foundVMsVisibility = "visibility_off"
    foundVCsList = list()
    for mac in macList:
        # message to be displayed to user on live messages page
        liveMessage = "searching for vm that has MAC: '{}'".format(mac)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        for i, vmInstance in enumerate(vmObjsList):
            # print(vmInstance.name)
            # vmNICDevList = list()
            vmMac = None
            foundMac = False
            loop = 0

            try:
                vmHardwardDevs = vmInstance.config.hardware.device
            except:
                vmHardwardDevs = list()

            for dev in vmHardwardDevs:
                try:
                    vmDevLabel = dev.deviceInfo.label
                except:
                    vmDevLabel = "unable to determine"

                if hasattr(dev, 'macAddress'):
                    try:
                        vmMac = str(dev.macAddress)
                    except:
                        vmMac = "unable to determine"

            if vmMac == mac:
                # message to be displayed to user on live messages page
                liveMessage = "MAC address: '{}' belongs to VM: '{}'".format(mac, vmInstance.name)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                foundVmObjsList.append(vmInstance)
                foundMac = True

                try:
                    parentInstance = vmInstance.parent
                except:
                    pass

                if parentInstance != None:
                    while True:
                        loop = loop + 1
                        try:
                            checkState = isinstance(parentInstance, vim.Datacenter)
                        except:
                            pass

                        if checkState == True:
                            try:
                                vc = parentInstance.name
                                foundVCsList.append(vc)
                                break
                            except:
                                pass
                        else:
                            try:
                                parentInstance = parentInstance.parent
                            except:
                                pass

                        if loop == maxLoops:
                            break


            if foundMac == True:
                break
            else:
                pass

        if foundMac == False:
            cantFindVMsList.append(mac)
            cantFindVMsVCInfoVisibility = "visibility_on"

    if len(foundVmObjsList) > 0:
        foundVMsVisibility = "visibility_on"

    session['cant_find_vms_list'] = cantFindVMsList
    session['cant_find_vms_vc_visibility'] = cantFindVMsVCInfoVisibility
    session['found_vms_visibility'] = foundVMsVisibility
    session['found_vcs_list'] = foundVCsList

    return foundVmObjsList


def getVMInstanceByIP(vmObjsList, ipList):
    cantFindVMsList = list()
    cantFindVMsVCInfoVisibility = "visibility_off"
    foundVmObjsList = list()
    foundVMsVisibility = "visibility_off"
    foundVCsList = list()
    for ip in ipList:
        # message to be displayed to user on live messages page
        liveMessage = "searching for vm that has IP: '{}'".format(ip)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        for i, vmInstance in enumerate(vmObjsList):
            foundIP = False
            loop = 0

            try:
                vmIP = vmInstance.guest.ipAddress
            except:
                vmIP = None

            if vmIP == ip:
                # message to be displayed to user on live messages page
                liveMessage = "IP address: '{}' belongs to VM: '{}'".format(ip, vmInstance.name)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                foundVmObjsList.append(vmInstance)
                foundIP = True

                try:
                    parentInstance = vmInstance.parent
                except:
                    pass

                if parentInstance != None:
                    while True:
                        loop = loop + 1
                        try:
                            checkState = isinstance(parentInstance, vim.Datacenter)
                        except:
                            pass

                        if checkState == True:
                            try:
                                vc = parentInstance.name
                                foundVCsList.append(vc)
                                break
                            except:
                                pass
                        else:
                            try:
                                parentInstance = parentInstance.parent
                            except:
                                pass

                        if loop == maxLoops:
                            break


            if foundIP == True:
                break
            else:
                pass

        if foundIP == False:
            cantFindVMsList.append(mac)
            cantFindVMsVCInfoVisibility = "visibility_on"

    if len(foundVmObjsList) > 0:
        foundVMsVisibility = "visibility_on"

    session['cant_find_vms_list'] = cantFindVMsList
    session['cant_find_vms_vc_visibility'] = cantFindVMsVCInfoVisibility
    session['found_vms_visibility'] = foundVMsVisibility
    session['found_vcs_list'] = foundVCsList

    return foundVmObjsList


def getVMvSphereInstancesWithVC(user, password, searchDict):
    vmObjsList = list()
    siList = list()
    dcObjsList = list()

    for key, value in searchDict.items():
        vc = key
        vmsList = value

        for vm in vmsList:
            # message to be displayed to user on live messages page
            liveMessage = "obtaining vsphere object for VM: '{}' in VC: '{}'".format(vm, vc)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            loop = 0
            foundVM = False
            # set to lowercase, as VM's are lower case in most cases in our vcenters
            vm = vm.lower()
            if domain in vm:
                vm = vm.replace("." + domain, "")

            vmObj = None

            try:
                si = ServiceInstance(vc, user, password)
                content = si.content
            except:
                si = None

            try:
                vmObj = getVMInstanceByName(si, vm)
                if vmObj:
                    # message to be displayed to user on live messages page
                    liveMessage = "vsphere object successfully set for VM: '{}'".format(vm)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    foundVM = True
                    vmObjsList.append(vmObj)
                    siList.append(si)
                    # finding hosting dc
                    try:
                        parentInstance = vmObj.parent
                    except:
                        pass

                    # message to be displayed to user on live messages page
                    liveMessage = "finding DC for VM: '{}'".format(vm)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)
                    if parentInstance != None:
                        while True:
                            loop = loop + 1
                            try:
                                checkState = isinstance(parentInstance, vim.Datacenter)
                            except:
                                pass

                            if checkState == True:
                                try:
                                    dc = parentInstance
                                    dcObjsList.append(dc)
                                except:
                                    pass
                                break
                            else:
                                try:
                                    parentInstance = parentInstance.parent
                                except:
                                    pass

                            if loop == maxLoops:
                                break

                    # message to be displayed to user on live messages page
                    liveMessage = "{}".format(stars)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

            except:
                pass


            if foundVM == False:
                # message to be displayed to user on live messages page
                liveMessage = "{}".format(stars)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
                # set to upper case, in case VM is upper case in our vcenters
                vm = vm.upper()

                if domain.upper() in vm:
                    vm = vm.replace("." + domain.upper(),"")

                vmObj = None

                try:
                    si = ServiceInstance(vc, user, password)
                    content = si.content
                except:
                    si = None
                try:
                    vmObj = getVMInstanceByName(si, vm)
                    if vmObj:
                        # message to be displayed to user on live messages page
                        liveMessage = "vsphere object successfully set for VM: '{}'".format(vm)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                        foundVM = True
                        vmObjsList.append(vmObj)
                        foundVCsList.append(vc)
                        siList.append(si)
                        # finding hosting dc
                        try:
                            parentInstance = vmObj.parent
                        except:
                            pass

                        # message to be displayed to user on live messages page
                        liveMessage = "finding DC for VM: '{}'".format(vm)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                        if parentInstance != None:
                            while True:
                                loop = loop + 1
                                try:
                                    checkState = isinstance(parentInstance, vim.Datacenter)
                                except:
                                    # checkState = False
                                    pass

                                if checkState == True:
                                    try:
                                        dc = parentInstance
                                        dcObjsList.append(dc)
                                    except:
                                        pass
                                    break
                                else:
                                    try:
                                        parentInstance = parentInstance.parent
                                    except:
                                        pass

                                if loop == maxLoops:
                                    break

                        # message to be displayed to user on live messages page
                        liveMessage = "{}".format(stars)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                except:
                    pass


    vmVsphereInstancesList = [vmObjsList, dcObjsList, siList]
    return vmVsphereInstancesList


def getVMvSphereInstances(user, password, searchList):
    vmVsphereInstancesList = list()
    cantFindVMsList = list()
    vmObjsList = list()
    foundVCsList = list()
    dcObjsList = list()
    siList = list()
    vmsList = list()
    print()

    foundVMsVisibility = "visibility_off"
    cantFindVMsVCInfoVisibility = "visibility_off"

    if ':' in searchList:
        macsList = searchList
    else:
        vmsList = searchList

    # message to be displayed to user on live messages page
    liveMessage = "finding where vms: {} reside.".format(vmsList)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "please standby...."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    for vm in vmsList:
        print("*" * 70)
        i = 0
        loop = 0
        foundVM = False

        # set to lowercase, as VM's are lower case in most cases in our vcenters
        vm = vm.lower()
        # message to be displayed to user on live messages page
        liveMessage = "finding vc for vm: '{}'".format(vm)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)
        if domain in vm:
            vm = vm.replace("." + domain,"")

        for vc in vcsList:
            # message to be displayed to user on live messages page
            liveMessage = "checking VC: '{}'".format(vc)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            vmObj = None

            try:
                si = ServiceInstance(vc, user, password)
                content = si.content
            except:
                si = None
            try:
                vmObj = getVMInstanceByName(si, vm)
                if vmObj:
                    foundVM = True
                    # message to be displayed to user on live messages page
                    liveMessage = "VM: {} resides in VC: {}".format(vm, vc)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

                    vmObjsList.append(vmObj)
                    foundVCsList.append(vc)
                    siList.append(si)
                    # finding hosting dc
                    try:
                        parentInstance = vmObj.parent
                    except:
                        pass

                    if parentInstance != None:
                        while True:
                            loop = loop + 1
                            try:
                                checkState = isinstance(parentInstance, vim.Datacenter)
                            except:
                                # checkState = False
                                pass

                            if checkState == True:
                                try:
                                    dc = parentInstance
                                    dcObjsList.append(dc)
                                except:
                                    pass
                                break
                            else:
                                try:
                                    parentInstance = parentInstance.parent
                                except:
                                    pass

                            if loop == maxLoops:
                                break

                    # message to be displayed to user on live messages page
                    liveMessage = "{}".format(stars)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)
                    break

            except:
                pass

        if foundVM == False:
            # message to be displayed to user on live messages page
            liveMessage = "{}".format(stars)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            # set to upper case, in case VM is upper case in our vcenters
            vm = vm.upper()
            # message to be displayed to user on live messages page
            liveMessage = "finding vc for vm: '{}'".format(vm)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            if domain.upper() in vm:
                vm = vm.replace("." + domain.upper(),"")

            for vc in vcsList:
                # message to be displayed to user on live messages page
                liveMessage = "checking VC: '{}'".format(vc)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
                vmObj = None

                try:
                    si = ServiceInstance(vc, user, password)
                    content = si.content
                except:
                    si = None
                try:
                    vmObj = getVMInstanceByName(si, vm)
                    if vmObj:
                        foundVM = True
                        # message to be displayed to user on live messages page
                        liveMessage = "VM: {} resides in VC: {}".format(vm, vc)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)

                        vmObjsList.append(vmObj)
                        foundVCsList.append(vc)
                        siList.append(si)
                        # finding hosting dc
                        try:
                            parentInstance = vmObj.parent
                        except:
                            pass

                        if parentInstance != None:
                            while True:
                                loop = loop + 1
                                try:
                                    checkState = isinstance(parentInstance, vim.Datacenter)
                                except:
                                    # checkState = False
                                    pass

                                if checkState == True:
                                    try:
                                        dc = parentInstance
                                        dcObjsList.append(dc)
                                    except:
                                        pass
                                    break
                                else:
                                    try:
                                        parentInstance = parentInstance.parent
                                    except:
                                        pass

                                if loop == maxLoops:
                                    break

                        # message to be displayed to user on live messages page
                        liveMessage = "{}".format(stars)
                        print(liveMessage)
                        print()
                        general.showUserMessage(liveMessage)
                        break

                    else:
                        i = i + 1

                except:
                    pass

                if i == numVCs:
                    cantFindVMsList.append(vm)

    if len(cantFindVMsList) > 0:
        print()
        cantFindVMsVCInfoVisibility = "visibility_on"
        print("can't find the below VM's:")
        for vm in cantFindVMsList:
            print(vm)

    if len(vmObjsList) > 0:
        foundVMsVisibility = "visibility_on"

    session['cant_find_vms_list'] = cantFindVMsList
    session['found_vms_visibility'] = foundVMsVisibility
    session['found_vcs_list'] = foundVCsList
    session['cant_find_vms_vc_visibility'] = cantFindVMsVCInfoVisibility
    vmVsphereInstancesList = [vmObjsList, dcObjsList, siList]

    return vmVsphereInstancesList


def displayVMs(vmObjsList):
    # message to be displayed to user on live messages page
    liveMessage = "display requested VM/s:".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    vmNICPrefixLabel = "Network adapter "
    try:
        error = session.get('flash_errors')
    except:
        error = None
        session['flash_errors'] = error
    listOfVMInfoLists = list()
    loop = 0
    dc = str()
    foundVCsList = session.get('found_vcs_list')

    for i, vmInstance in enumerate(vmObjsList):
        multiVMsInfoList = list()
        vmNICNamesList = list()
        vmNICStatesList = list()
        vmNICDevList = list()
        vmMac = None

        try:
            vc = foundVCsList[i]
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vc = "unable to determine"

        try:
            vmParentFolder = vmInstance.parent.name
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vmParentFolder = "unable to determine"

        try:
            vmUUID = vmInstance.config.uuid
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vmUUID = "unable to determine"

        try:
            vmName = vmInstance.config.name
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vmName = "unable to determine"

        try:
            vmPowerState = vmInstance.runtime.powerState
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vmPowerState = "unable to determine"

        try:
            vmRunningState = vmInstance.guest.guestState
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vmRunningState = "unable to determine"

        try:
            vmIP = vmInstance.guest.ipAddress
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vmIP = "unable to determine"

        try:
            vmOS = vmInstance.guest.guestFullName
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vmOS = "unable to determine"

        try:
            vmNumCPU = vmInstance.summary.config.numCpu
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vmNumCPU = "unable to determine"

        try:
            vmNumMem = vmInstance.summary.config.memorySizeMB
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vmNumMem = "unable to determine"

        try:
            vmHardwardDevs = vmInstance.config.hardware.device
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            vmHardwardDevs = list()

        for dev in vmHardwardDevs:
            try:
                vmDevLabel = dev.deviceInfo.label
            except Exception as e:
                exceptionMessage = "Exception caught: '{}'".format(str(e))
                print(exceptionMessage)
                general.showUserMessage(exceptionMessage)
                vmDevLabel = "unable to determine"
            try:
                if isinstance(dev, vim.vm.device.VirtualEthernetCard) \
                    and vmNICPrefixLabel in vmDevLabel:
                    vmNICDevList.append(dev)
            except Exception as e:
                exceptionMessage = "Exception caught: '{}'".format(str(e))
                print(exceptionMessage)
                general.showUserMessage(exceptionMessage)

            if hasattr(dev, 'macAddress'):
                try:
                    vmMac = str(dev.macAddress)
                except Exception as e:
                    exceptionMessage = "Exception caught: '{}'".format(str(e))
                    print(exceptionMessage)
                    general.showUserMessage(exceptionMessage)
                    vmMac = "unable to determine"

        vmNICNamesList = list()
        vmNICStatesList = list()

        # message to be displayed to user on live messages page
        liveMessage = lines
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "VM Name:                {}".format(vmName)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "VM Parent Folder:       {}".format(vmParentFolder)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "VM UUID:                {}".format(vmUUID)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "Power State:            {}".format(vmPowerState)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "Running State:          {}".format(vmRunningState)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "VM IP:                  {}".format(vmIP)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "VM MAC:                 {}".format(vmMac)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "VM OS:                  {}".format(vmOS)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "Num CPU's:              {}".format(str(vmNumCPU))
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        liveMessage = "Memory (MB):            {}".format(str(vmNumMem))
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)



        for vmNICDev in vmNICDevList:
            # message to be displayed to user on live messages page
            liveMessage = "VM NIC device:          {}".format(str(vmNICDev.deviceInfo.label))
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            vmNICNamesList.append(str(vmNICDev.deviceInfo.label))

            liveMessage = "VM NIC Connected:       {}".format(str(vmNICDev.connectable.connected))
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            vmNICStatesList.append(str(vmNICDev.connectable.connected))

        try:
            multiVMsInfoList.append(list((str(vmName), str(vc), str(vmParentFolder),
                str(vmUUID), str(vmPowerState), str(vmRunningState), str(vmIP),
                str(vmMac), str(vmOS), str(vmNumCPU), str(vmNumMem),
                str(vmNICNamesList), str(vmNICStatesList))))

            listOfVMInfoLists.append(multiVMsInfoList)

            session['list_of_VM_info_Lists'] = listOfVMInfoLists
        except Exception as e:
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(exceptionMessage)
            general.showUserMessage(exceptionMessage)
            session['list_of_VM_info_Lists'] = [[]]

    # message to be displayed to user on live messages page
    liveMessage = "{}".format(stars)
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)


def mkdirTask(base_obj, dir_name):
    try:
        return base_obj.CreateFolder(dir_name)
    except (vim.fault.InvalidName) as e:
        print(e)
        import sys
        sys.exit()


def createFolder(content, base_obj, folder_path):

    folder_path_parts = folder_path.strip('/').split('/')

    for path_part in folder_path_parts:
        if base_obj.childEntity:
            for y, child_obj in enumerate(base_obj.childEntity):
                if child_obj.name == path_part:
                    base_obj = child_obj
                    break
                elif y >= len(base_obj.childEntity)-1:
                    base_obj = mkdirTask(base_obj, path_part)
                    break
        else:
            base_obj = mkdirTask(base_obj, path_part)


def folderActions(vmDeleteDatesDict, dcObjsList, siList, vmObjsList):
    vmDelBit = "DEL"
    coNum = session.get('change_order_number')
    for i, vmInstance in enumerate(vmObjsList):
        vmName = vmInstance.config.name
        vmDeleteDate = vmDeleteDatesDict[vmName]
        folderName = vmDelBit + "_" + vmDeleteDate + "_" + coNum
        folderInstance = None
        folderExists = False
        fullPathFolderName = baseDeleteFolder + "/" + folderName
        si = siList[i]
        content = si.content
        newFolderInstance = getVsphereObj(content, [vim.Folder], folderName)

        # message to be displayed to user on live messages page
        liveMessage = "checking if folder: '{}' already exists".format(folderName)
        print(liveMessage)
        print()
        general.showUserMessage(liveMessage)

        # check if folder already exists, if not, create it.
        if newFolderInstance:
            # message to be displayed to user on live messages page
            liveMessage = "Folder: '{}' already exists".format(folderName)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            folderExists = True
            folderInstance = newFolderInstance
        elif newFolderInstance == None:
            # message to be displayed to user on live messages page
            liveMessage = "Folder: '{}' does not exists".format(folderName)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            liveMessage = "attempting to create: '{}' in '{}'".format(folderName, baseDeleteFolder)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            createFolder(content, dcObjsList[i].vmFolder, fullPathFolderName)

            liveMessage = "checking if create was successful..."
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            folderInstance = getVsphereObj(content, [vim.Folder], folderName)
            if folderInstance:
                # message to be displayed to user on live messages page
                liveMessage = "Successfully created folder: '{}' in '{}'".format(folderName, baseDeleteFolder)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
                folderExists = True
            else:
                liveMessage = "Folder: '{}' probably wasn't created, please check manually...".format(folderName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
        else:
            liveMessage = "I don't know what you want me to do... Askies neh..."
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
        print()

        # move VM/s into folder:
        if folderExists == True:
            vmName = vmInstance.config.name
            vmParentFolder = vmInstance.parent

            if folderInstance == vmParentFolder:
                # message to be displayed to user on live messages page
                liveMessage = "VM: '{}' already exists in folder: '{}'".format(vmName, fullPathFolderName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                liveMessage = "Not moving VM: '{}'.".format(vmName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

            elif folderInstance != vmParentFolder:
                # message to be displayed to user on live messages page
                liveMessage = "attempting to move VM: '{}' into '{}'".format(vmName, fullPathFolderName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

                # folder move action: moves the VM Instance into the folder.
                try:
                    folderInstance.MoveInto([vmInstance])
                    liveMessage = "successfully moved VM: '{}' to '{}'".format(vmName, fullPathFolderName)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)
                except:
                    liveMessage = "unable to move vm: '{}' into '{}'".format(vmName, fullPathFolderName)
                    print(liveMessage)
                    print()
                    general.showUserMessage(liveMessage)

    # message to be displayed to user on live messages page
    liveMessage = lines
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)


# nicState = connect /  disconnect / delete
def changeVMNICState(vmObjsList, nicState):
    vmNICPrefixLabel = "Network adapter "

    for vmInstance in vmObjsList:
        vmNICDevList = list()
        vmName = vmInstance.config.name
        vmHardwardDevs = vmInstance.config.hardware.device

        for dev in vmHardwardDevs:
            vmDevLabel = dev.deviceInfo.label

            if isinstance(dev, vim.vm.device.VirtualEthernetCard) \
                and vmNICPrefixLabel in vmDevLabel:
                vmNICDevList.append(dev)

        for vmNICDev in vmNICDevList:
            vmNICSpec = vim.vm.device.VirtualDeviceSpec()

            if nicState == 'delete':
                vmNICSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
                vmNICSpec.device = vmNICDev
            else:
                vmNICSpec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit

            vmNICSpec.device = vmNICDev
            vmNICSpec.device.key = vmNICDev.key
            vmNICSpec.device.macAddress = vmNICDev.macAddress
            vmNICSpec.device.backing = vmNICDev.backing
            vmNICSpec.device.backing.port = vmNICDev.backing.port
            vmNICSpec.device.wakeOnLanEnabled = vmNICDev.wakeOnLanEnabled
            if nicState == 'connect':
                vmNICSpec.device.connectable.connected = True
                vmNICSpec.device.connectable.startConnected = True
            elif nicState == 'disconnect':
                vmNICSpec.device.connectable.connected = False
                vmNICSpec.device.connectable.startConnected = False
            else:
                connectable = vmNICDev.connectable

            spec = vim.vm.ConfigSpec()
            spec.deviceChange = [vmNICSpec]
            # message to be displayed to user on live messages page
            liveMessage = "VM: '{}', attempting to {} NIC: '{}'...".format(vmName, nicState ,vmDevLabel)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            try:
                vmNICUpdateStateTask = vmInstance.ReconfigVM_Task(spec=spec)

                # message to be displayed to user on live messages page
                liveMessage = "VM: '{}' NIC: '{}' {} successful...".format(vmName, vmDevLabel, nicState)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
            except:
                liveMessage = "VM: '{}' unable to {} NIC: '{}'...".format(vmName, nicState, vmDevLabel)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
    # message to be displayed to user on live messages page
    liveMessage = lines
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)


def powerDownVM(vmObjsList, siList):
    for i, vmInstance in enumerate(vmObjsList):
        si = siList[i]

        try:
            vmPowerState = vmInstance.runtime.powerState
            vmName = vmInstance.config.name
        except Exception as e:
            liveMessage = "Unable to determine power state for VM: '{}'.".format(vmName)
            exceptionMessage = "Exception caught: '{}'".format(str(e))
            print(liveMessage)
            print()
            print(exceptionMessage)
            print()
            general.showUserMessage(liveMessage)
            general.showUserMessage(exceptionMessage)

        if vmPowerState == vim.VirtualMachinePowerState.poweredOn:
            # message to be displayed to user on live messages page
            liveMessage = "VM: '{}' is currently powered on.".format(vmName)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            liveMessage = "attempting to power it down..."
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            powerDownTask = vmInstance.PowerOff()
            liveMessage = "checking if power down was successful..."
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            # wait 5 secs, for vsphere / vm to catch up...
            sleep(5)
            # reset vmInstance variable, after power down.
            vmInstance = getVMInstanceByName(si, vmName)
            # get power state
            getVMPowerState = vmInstance.runtime.powerState
            # check if power down task was successful
            if getVMPowerState == "poweredOff":
                # message to be displayed to user on live messages page
                liveMessage = "VM: '{}' successfully powered down...".format(vmName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)
            else:
                liveMessage = "unable to determine VM: '{}' current power state.".format(vmName)
                print(liveMessage)
                print()
                general.showUserMessage(liveMessage)

        elif vmPowerState == vim.VirtualMachinePowerState.suspended:
            # message to be displayed to user on live messages page
            liveMessage = "VM: '{}' is currently suspended.".format(vmName)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            liveMessage = "leaving VM as is"
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

        elif vmPowerState == vim.VirtualMachinePowerState.poweredOff:
            # message to be displayed to user on live messages page
            liveMessage = "VM: '{}' is currently powered off.".format(vmName)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            liveMessage = "leaving VM as is"
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)
        else:
            # message to be displayed to user on live messages page
            liveMessage = "unable to determine power state of VM: '{}'.".format(vmName)
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

            liveMessage = "leaving VM as is"
            print(liveMessage)
            print()
            general.showUserMessage(liveMessage)

    liveMessage = lines
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)


def vmDecommActions(vmDeleteDatesDict, dcObjsList, siList, vmObjsList, vmNICState):
    # message to be displayed to user on live messages page
    liveMessage = lines
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "VM folder actions step"
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    # create delete folder, if not there already.
    # then move vm/s into it.
    folderActions(vmDeleteDatesDict, dcObjsList, siList, vmObjsList)

    liveMessage = lines
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")


    # message to be displayed to user on live messages page
    liveMessage = lines
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "VM NIC state change step"
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    # disconnect the vm/s nic/s.
    changeVMNICState(vmObjsList, vmNICState)

    liveMessage = lines
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")

    # message to be displayed to user on live messages page
    liveMessage = lines
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "VM power down step"
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    # power down the vm/s.
    powerDownVM(vmObjsList, siList)

    liveMessage = lines
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)
    general.showUserMessage(".")


def verifyVsphereDecomm(vmObj, vmDeleteDatesDict):
    # message to be displayed to user on live messages page
    liveMessage = stars
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = "Verify if VM is down in Vsphere Method..."
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    liveMessage = stars
    print(liveMessage)
    print()
    general.showUserMessage(liveMessage)

    vmDelBit = "DEL"
    coNum = session.get('change_order_number')
    vmName = vmObj.config.name
    vmDeleteDate = vmDeleteDatesDict[vmName]
    decommFolder = vmDelBit + "_" + vmDeleteDate + "_" + coNum
    vmPoweredOffState = "poweredOff"
    activeStatus = "Currently active"
    deactivatedStatus = "Deactivated"
    vmPowerState = str()
    vmParentFolder = str()
    vsphereDecommStatus = str()

    try:
        vmPowerState = vmObj.runtime.powerState
        vmParentFolder = vmObj.parent.name
    except:
        pass

    if vmPowerState == vmPoweredOffState and vmParentFolder == decommFolder:
        vsphereDecommStatus = deactivatedStatus
    else:
        vsphereDecommStatus = activeStatus

    return vsphereDecommStatus
