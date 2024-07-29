#!/usr/bin/python3
from flask import session, Markup
from penguins.flaskdb import common_functions

# static variables
dbName = "tmc"
tmcDBTable = "tmc_main"
splunkHealthTable = "splunk_status"

def getAgentStatusData():
    # variables:
    selectResults = dict()
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
    getColumnNamesDBQuery = "SELECT column_name from information_schema.columns where table_name = '{}';".format(splunkHealthTable)
    cross_img_url = "/static/images/red-cross.png"
    tick_img_url = "/static/images/green-tick.png"
    null_img_url = "/static/images/grey-null.png"
    quoteStr = "\""
    startImgTag = "<img src="
    endImgTag = " width=\"30\" height=\"30\"></img>"
    tickEndImgTag = " width=\"34\" height=\"34\"></img>"

    try:
        splunkColumnNamesDict = common_functions.dbQueryExecutor(dbName, getColumnNamesDBQuery)
        splunkColumnNamesList = list()
        for key, value in splunkColumnNamesDict.items():
            splunkColumnNamesList = value

        splunkColumnNamesList.pop(0)
        splunkColumnNamesList.insert(0,'hostname')

        session['column_names'] = splunkColumnNamesList
        splunkHealthDict = common_functions.dbQueryExecutor(dbName, dbQuery)
        totalRecords = len(splunkHealthDict)
        session['total_records'] = totalRecords
        selectResults = splunkHealthDict

        updatedSelectResults = {}

        for key, values in splunkHealthDict.items():
            valuesList = list()

            if values[1] == False:
                values.pop(1)
                values.insert(1, "Null")

            if values[2] == False:
                values.pop(2)
                values.insert(2, "Null")

            for value in values:
                if value == False:
                    value = Markup(startImgTag + quoteStr + cross_img_url + quoteStr + endImgTag)
                elif value == True:
                    value = Markup(startImgTag + quoteStr + tick_img_url + quoteStr + tickEndImgTag)
                elif value == "Null":
                    value = Markup(startImgTag + quoteStr + null_img_url + quoteStr + tickEndImgTag)
                else:
                    value = str(value)

                valuesList.append(value)
            updatedSelectResults[key] = valuesList

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception: {}".format(str(e)))
        totalRecords = 0

    session['db_select_results'] = selectResults

    return updatedSelectResults
