#!/usr/bin/python3
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import psycopg2
from os import path
import ssl
import sneaky_apple_crumble
from cryptography.fernet import Fernet
import son_of_anton

knownVsphereVCsFile = "vsphere_vcenters"
flaskStaticDirLocation = "flasks/penguins_master/penguins/static/"

try:
    error = None
    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "..", flaskStaticDirLocation, knownVsphereVCsFile))
    openKnownVsphereVCsFile = open(filepath, "r")
    knownVsphereVCs = openKnownVsphereVCsFile.read().splitlines()
except:
    error = "unable to read file: " + filepath
    knownVsphereVCs = list()

if error:
    print(error)

vcsList = knownVsphereVCs
dbName = "vsphere"
dbTableName = "managed_vms"

receipe = {
    "lock_smith": "not happening today",
    "og_kush_repro": "not happening tomorrow",
    "bacon": "not happening ever......."
}

# Create service instance of VCenter/s
def ServiceInstance(vc, user, password):
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_NONE
    si = SmartConnect(host=vc, user=user, pwd=password, sslContext=context)
    return si


def getAllVMInstances(user, password):
    vimtype = [vim.VirtualMachine]
    vcsVMsDict = dict()

    for vc in vcsList:
        print("getting all VM's in VC:", vc)
        vmNamesList = list()
        vmObj = None
        si = None

        try:
            si = ServiceInstance(vc, user, password)
            content = si.content
            container = content.viewManager.CreateContainerView(
                content.rootFolder, vimtype, True)

            for vmObj in container.view:
                vmName = vmObj.name
                vmNamesList.append(vmName)

        except:
            si = None

        vcsVMsDict[vc] = vmNamesList

    return vcsVMsDict


def initialiseDBwithVsphereVMs(dbName, dbTableName):
# def initialiseDBwithVsphereVMs():
    print()
    print("Method to initialse table: '{}' on DB: '{}' with managed vsphere VM's.".format(dbTableName, dbName))
    print()
    conn = None
    cursor = None

    try:
        try:
            password = son_of_anton.getTheIngredients(receipe).decode()
        except Exception as e:
            password = None
            print("Error while obtaining the necessary ingredients for the receipe.")
            print("Exception caught: '{}'".format(e))

        conn = psycopg2.connect(user = "postgres",
                                password = password,
                                host = "x.x.x.x",
                                port = "5432",
                                database = dbName)
        cursor = conn.cursor()
    except Exception as e:
        print("Error while connecting to DB:", dbName)
        print("error:")
        print(e)

    try:
        auth_list = sneaky_apple_crumble.check_da_dip()
    except Exception as e:
        print("unable to run the apple crumble program...")
        print("error:")
        print(e)

    cipher_suite = Fernet(auth_list[1])

    try:
        vcsVMsDict = getAllVMInstances(cipher_suite.decrypt(auth_list[0]).decode(),
                        cipher_suite.decrypt(auth_list[2]).decode()
                        )
    except Exception as e:
        print("Error while connecting to vsphere")
        print("error:")
        print(e)

    for key, value in vcsVMsDict.items():
        vc = key
        vmsList = value
        print()
        print("now inserting found vm's for each vc: {}".format(vc))
        for vm in vmsList:
            insertQuery = "INSERT INTO {} ({}, {}) VALUES ('{}', '{}');".format(
                            dbTableName,
                            "vc_name",
                            "vm_name",
                            vc,
                            vm
            )
            try:
                cursor.execute(insertQuery)
                conn.commit()
            except Exception as e:
                print("Error while inserting vm: '{}' into DB: '{}' Table: '{}'".format(
                        vm,
                        dbName,
                        dbTableName
                        )
                )
                print("error:")
                print(e)
                cursor.execute("ROLLBACK")
                conn.commit()

    if(conn):
        dbConnDisconnect(conn)


def dbConnDisconnect(conn):
    try:
        conn.close()
        print("successfully disconnected from DB")
    except Exception as e:
        print("Error while disconnecting from DB")
        print("error:")
        print(e)


def updateVsphereDB(dbName, dbTableName):
    print()
    print("Method to update table: '{}' on DB: '{}' with any new managed vsphere VM's.".format(
            dbTableName,
            dbName
            )
    )
    print()
    conn = None
    cursor = None
    outputList = list()
    outputID = str()
    outputVC = str()
    outputServer = str()

    try:
        try:
            password = son_of_anton.getTheIngredients(receipe).decode()
        except Exception as e:
            password = None
            print("Error while obtaining the necessary ingredients for the receipe.")
            print("Exception caught: '{}'".format(e))

        conn = psycopg2.connect(user = "postgres",
                                password = password,
                                host = "x.x.x.x",
                                port = "5432",
                                database = dbName)
        cursor = conn.cursor()
    except Exception as e:
        print("Error while connecting to DB:", dbName)
        print("error:")
        print(e)

    try:
        auth_list = sneaky_apple_crumble.check_da_dip()
    except Exception as e:
        print("unable to run the apple crumble program...")
        print("error:")
        print(e)

    cipher_suite = Fernet(auth_list[1])

    try:
        vcsVMsDict = getAllVMInstances(cipher_suite.decrypt(auth_list[0]).decode(),
                        cipher_suite.decrypt(auth_list[2]).decode()
                        )
    except Exception as e:
        print("Error while connecting to vsphere")
        print("error:")
        print(e)

    for key, value in vcsVMsDict.items():
        vc = key
        vmsList = value
        print()
        print("checking each found vm in each vc: '{}', if it resides in our DB: '{}' in Table: '{}'".format(
                vc,
                dbName,
                dbTableName
                )
        )
        print()
        for vm in vmsList:
            selectQuery = "SELECT * FROM {} WHERE {} = '{}'".format(
                            dbTableName,
                            "vm_name",
                            vm
            )
            try:
                cursor.execute(selectQuery)
                output = cursor.fetchall()
                try:
                    outputList = output[0]
                    outputID = outputList[0]
                    outputVC = outputList[1]
                    outputServer = outputList[2]
                except:
                    outputID = ""
                    outputVC = ""
                    outputServer = ""
            except Exception as e:
                print("error:")
                print(e)

            if outputServer == "":
                insertQuery = "INSERT INTO {} ({}, {}) VALUES ('{}', '{}');".format(
                                dbTableName,
                                "vc_name",
                                "vm_name",
                                vc,
                                vm
                )
                try:
                    cursor.execute(insertQuery)
                    conn.commit()
                except Exception as e:
                    print("Error while inserting vm: '{}' into DB: '{}' Table: '{}'".format(
                            vm,
                            dbName,
                            dbTableName
                            )
                    )
                    print("error:")
                    print(e)
                    cursor.execute("ROLLBACK")
                    conn.commit()

            if outputID != "" and outputVC != "" and outputVC != vc:
                deleteQuery = "DELETE FROM {} WHERE {} = '{}';".format(
                                dbTableName,
                                "id",
                                outputID
                )
                try:
                    cursor.execute(deleteQuery)
                    conn.commit()
                except Exception as e:
                    print("Error while deleting vm: '{}' from DB: '{}' Table: '{}'".format(
                            vm,
                            dbName,
                            dbTableName
                            )
                    )
                    print("error:")
                    print(e)
                    cursor.execute("ROLLBACK")
                    conn.commit()

                insertQuery = "INSERT INTO {} ({}, {}) VALUES ('{}', '{}');".format(
                                dbTableName,
                                "vc_name",
                                "vm_name",
                                vc,
                                vm
                )
                try:
                    cursor.execute(insertQuery)
                    conn.commit()
                except Exception as e:
                    print("Error while inserting vm: '{}' into DB: '{}' Table: '{}'".format(
                            vm,
                            dbName,
                            dbTableName
                            )
                    )
                    print("error:")
                    print(e)
                    cursor.execute("ROLLBACK")
                    conn.commit()

    if(conn):
        dbConnDisconnect(conn)


updateVsphereDB(dbName, dbTableName)
# initialiseDBwithVsphereVMs(dbName, dbTableName)
