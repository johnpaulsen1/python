import math
from flask import session
from penguins.other_utils import general
from penguins.flaskdb import common_functions

def getGreatwallStats():
    addExtraForMaximum = 100

    dbName = "tmc"
    dbTableName = "tmc_main"
    dbQuery = "SELECT greatwall, COUNT(greatwall) AS greatwall_count FROM {} GROUP BY greatwall;".format(
        dbTableName
    )

    try:
        greatwallCountDict = common_functions.dbQueryExecutor(dbName, dbQuery)
        greatwallList = list()
        numGreatwallsList = list()

        for value in greatwallCountDict.values():
            greatwallList = greatwallCountDict.get('greatwall_s')
            numGreatwallsList = greatwallCountDict.get('num_greatwall_s')

        session['graph_labels'] = greatwallList
        session['graph_values'] = numGreatwallsList

        highestNum = max(numGreatwallsList)
        roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

        maxValue = roundedHighestNum + addExtraForMaximum

        session['graph_max_value'] = maxValue

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))
