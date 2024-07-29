import math
from flask import session
from penguins.other_utils import general
from penguins.flaskdb import common_functions

def getConfigManagerStats():
    addExtraForMaximum = 500

    dbName = "tmc"
    dbTableName = "tmc_main"
    dbQuery = "SELECT config_manager, COUNT(config_manager) AS config_manager_count FROM {} GROUP BY config_manager;".format(
        dbTableName
    )

    try:
        configManagersCountDict = common_functions.dbQueryExecutor(dbName, dbQuery)
        configManagersList = list()
        numManagedList = list()

        for value in configManagersCountDict.values():
            configManagersList = configManagersCountDict.get('config_managers')
            numManagedList = configManagersCountDict.get('num_managed')

        session['graph_labels'] = configManagersList
        session['graph_values'] = numManagedList

        highestNum = max(numManagedList)
        roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

        maxValue = roundedHighestNum + addExtraForMaximum

        session['graph_max_value'] = maxValue

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))
