import math
from flask import session
from penguins.other_utils import general
from penguins.flaskdb import common_functions

def getServerTypeStats():
    addExtraForMaximum = 100

    dbName = "tmc"
    dbTableName = "tmc_main"
    dbQuery = "SELECT host_type, COUNT(host_type) AS host_type_count FROM {} GROUP BY host_type;".format(
        dbTableName
    )

    try:
        serverTypeCountDict = common_functions.dbQueryExecutor(dbName, dbQuery)
        serverTypeList = list()
        numServerTypesList = list()

        for value in serverTypeCountDict.values():
            serverTypeList = serverTypeCountDict.get('server_types')
            numServerTypesList = serverTypeCountDict.get('num_server_types')

        session['graph_labels'] = serverTypeList
        session['graph_values'] = numServerTypesList

        highestNum = max(numServerTypesList)
        roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

        maxValue = roundedHighestNum + addExtraForMaximum

        session['graph_max_value'] = maxValue

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))
