import math
from flask import session
from penguins.other_utils import general
from penguins.flaskdb import common_functions

def getOSstats():
    addExtraForMaximum = 50
    dbName = "tmc"
    dbTableName = "tmc_main"
    dbQuery = "SELECT DISTINCT osfamily FROM {};".format(
                        dbTableName
    )

    try:
        osFamiliesDict = common_functions.dbQueryExecutor(dbName, dbQuery)
        session['os_families_dict'] = osFamiliesDict
        maxValueDict = dict()

        for key, valueDict in osFamiliesDict.items():
            numOSFamiliesList = list()
            for value in valueDict.values():
                numOSFamiliesList.append(value)

            highestNum = max(numOSFamiliesList)
            roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

            if highestNum <= 100:
                addExtraForMaximum = 0
            elif highestNum <= 200:
                addExtraForMaximum = 0
            elif highestNum <= 400:
                addExtraForMaximum = 20
            elif highestNum <= 800:
                addExtraForMaximum = 50
            elif highestNum <= 1000:
                addExtraForMaximum = 50
            elif highestNum <= 1500:
                addExtraForMaximum = 100
            elif highestNum <= 3000:
                addExtraForMaximum = 200
            elif highestNum <= 5000:
                addExtraForMaximum = 250

            maxValue = roundedHighestNum + addExtraForMaximum
            maxValueDict[key] = maxValue

        session['graph_max_value_dict'] = maxValueDict

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))
