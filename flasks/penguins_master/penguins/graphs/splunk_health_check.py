import math
from flask import session
from penguins.other_utils import general
from penguins.flaskdb import common_functions

def getSplunkHealthCheckData():
    addExtraForMaximum = 50

    dbName = "tmc"
    tmcDBTable = "tmc_main"
    splunkHealthTable = "splunk_status"
    dbQuery = "SELECT {}.id, {}.hostname, {}.* FROM {} \
                INNER JOIN {} ON {}.splunk_id = {}.id ORDER BY {}.id;".format(
                tmcDBTable,
                tmcDBTable,
                splunkHealthTable,
                tmcDBTable,
                splunkHealthTable,
                tmcDBTable,
                splunkHealthTable,
                tmcDBTable
                )
    healthyLabel = "healthy"
    unHealthyLabel = "un-healthy"
    splunkHealthDict = dict()
    heathlyCount = 0
    unHeathlyCount = 0


    try:
        splunkHealthDataDict = common_functions.dbQueryExecutor(dbName, dbQuery)

        for valueList in splunkHealthDataDict.values():
            healthKeeper = False

            hostname = valueList[0]
            managed = valueList[1]
            selfManaged = valueList[2]

            installed = valueList[3]
            if installed:
                healthKeeper = True
            else:
                healthKeeper = False

            latestInstalled = valueList[4]
            if latestInstalled and healthKeeper:
                healthKeeper = True
            else:
                healthKeeper = False

            versionInstalled = valueList[5]

            running = valueList[6]
            if running and healthKeeper:
                healthKeeper = True
            else:
                healthKeeper = False

            # handshake = valueList[7]
            # if handshake and healthKeeper:
            #     healthKeeper = True
            # else:
            #     healthKeeper = False

            varlogAccess = valueList[8]
            if varlogAccess and healthKeeper:
                healthKeeper = True
            else:
                healthKeeper = False

            varlogMessagesAccess = valueList[9]
            if varlogMessagesAccess and healthKeeper:
                healthKeeper = True
            else:
                healthKeeper = False

            varlogSecureAccess = valueList[10]
            if varlogSecureAccess and healthKeeper:
                healthKeeper = True
            else:
                healthKeeper = False

            osLogsPopulated = valueList[11]
            if osLogsPopulated and healthKeeper:
                healthKeeper = True
            else:
                healthKeeper = False

            frgConfDirExists = valueList[12]
            if frgConfDirExists and healthKeeper:
                healthKeeper = True
            else:
                healthKeeper = False


            if healthKeeper:
                heathlyCount += 1
                splunkHealthDict[healthyLabel] = heathlyCount
            elif healthKeeper == False:
                unHeathlyCount += 1
                splunkHealthDict[unHealthyLabel] = unHeathlyCount

        labels = list(splunkHealthDict.keys())
        values = list(splunkHealthDict.values())

        session['graph_labels'] = labels
        session['graph_values'] = values

        highestNum = max(values)
        roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

        maxValue = roundedHighestNum + addExtraForMaximum

        session['graph_max_value'] = maxValue

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))
