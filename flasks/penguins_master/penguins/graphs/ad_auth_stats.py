import math
from flask import session
from penguins.other_utils import general
from penguins.flaskdb import common_functions

def getADAuthStats():
    addExtraForMaximum = 50

    dbName = "tmc"
    dbTableName = "tmc_main"
    dbQuery = "SELECT ad_auth, COUNT(ad_auth) AS ad_auth_count FROM {} GROUP BY ad_auth;".format(
        dbTableName
    )

    try:
        adAuthCountDict = common_functions.dbQueryExecutor(dbName, dbQuery)
        adAuthList = list()
        numADAuthsList = list()

        for value in adAuthCountDict.values():
            adAuthList = adAuthCountDict.get('ad_auth_s')
            numADAuthsList = adAuthCountDict.get('num_ad_auth_s')

        labelsList = list()
        for label in adAuthList:
            if label == 'True' or label == True:
                label = 'Yes'
            elif label == 'False' or label == False:
                label = 'No'
            else:
                label = label

            labelsList.append(label)

        session['graph_labels'] = labelsList
        session['graph_values'] = numADAuthsList

        highestNum = max(numADAuthsList)
        roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

        maxValue = roundedHighestNum + addExtraForMaximum

        session['graph_max_value'] = maxValue

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))
