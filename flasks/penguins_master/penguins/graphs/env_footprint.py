import math
from flask import session
from penguins.other_utils import general
from penguins.flaskdb import common_functions

def getEnvFootprintStats():
    addExtraForMaximum = 50

    dbName = "tmc"
    dbTableName = "tmc_main"
    dbQuery = "SELECT role, COUNT(role) AS role_count FROM {} GROUP BY role;".format(
        dbTableName
    )

    try:
        envCountDict = common_functions.dbQueryExecutor(dbName, dbQuery)
        envList = list()
        numEnvsList = list()

        for value in envCountDict.values():
            envList = envCountDict.get('env_s')
            numEnvsList = envCountDict.get('num_env_s')

        session['graph_labels'] = envList
        session['graph_values'] = numEnvsList

        highestNum = max(numEnvsList)
        roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

        maxValue = roundedHighestNum + addExtraForMaximum

        session['graph_max_value'] = maxValue

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))
