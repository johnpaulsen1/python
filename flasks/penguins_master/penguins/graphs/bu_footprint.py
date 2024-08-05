import math
from flask import session
from penguins.other_utils import general
from penguins.flaskdb import common_functions

def getBUFootprintStats():
    addExtraForMaximum = 0

    dbName = "tmc"
    dbTableName = "tmc_main"
    dbQuery = "SELECT bu, COUNT(bu) AS bu_count FROM {} GROUP BY bu;".format(
        dbTableName
    )

    try:
        buCountDict = common_functions.dbQueryExecutor(dbName, dbQuery)
        buList = list()
        numBUsList = list()

        for value in buCountDict.values():
            buList = buCountDict.get('bu_s')
            numBUsList = buCountDict.get('num_bu_s')

        session['graph_labels'] = buList
        session['graph_values'] = numBUsList

        highestNum = max(numBUsList)
        roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

        maxValue = roundedHighestNum + addExtraForMaximum

        session['graph_max_value'] = maxValue

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))
