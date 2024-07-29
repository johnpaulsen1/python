#!/usr/bin/python3
from flask import session, Markup
from penguins.flaskdb import common_functions

# static variables
dbName = "tmc"
tmcDBTable = "tmc_main"
flexeraHealthTable = "flexera_status"

def getAgentStatusData():
    # variables:
    selectResults = dict()
    dbQuery = "SELECT {}.id, {}.hostname, {}.* FROM {} \
                INNER JOIN {} ON {}.id = {}.id ORDER BY {}.id;".format(
                tmcDBTable,
                tmcDBTable,
                flexeraHealthTable,
                tmcDBTable,
                flexeraHealthTable,
                tmcDBTable,
                flexeraHealthTable,
                tmcDBTable
                )
    getColumnNamesDBQuery = "SELECT column_name from information_schema.columns where table_name = '{}';".format(flexeraHealthTable)
    cross_img_url = "/static/images/red-cross.png"
    tick_img_url = "/static/images/green-tick.png"
    null_img_url = "/static/images/grey-null.png"
    quoteStr = "\""
    startImgTag = "<img src="
    endImgTag = " width=\"30\" height=\"30\"></img>"
    tickEndImgTag = " width=\"34\" height=\"34\"></img>"

    try:
        flexeraColumnNamesDict = common_functions.dbQueryExecutor(dbName, getColumnNamesDBQuery)
        flexeraColumnNamesList = list()
        for key, value in flexeraColumnNamesDict.items():
            flexeraColumnNamesList = value

        flexeraColumnNamesList.pop(0)
        flexeraColumnNamesList.insert(0,'hostname')

        session['column_names'] = flexeraColumnNamesList
        flexeraHealthDict = common_functions.dbQueryExecutor(dbName, dbQuery)
        totalRecords = len(flexeraHealthDict)
        session['total_records'] = totalRecords
        selectResults = flexeraHealthDict

        updatedSelectResults = {}

        for key, values in flexeraHealthDict.items():
            valuesList = list()

            for value in values:
                if value == False or value.lower() == "not running" or value.lower() == "not installed" or value.lower() == "no" or value.lower() == "none":
                    value = Markup(startImgTag + quoteStr + cross_img_url + quoteStr + endImgTag)
                elif value == True or value.lower() == "running" or value.lower() == "installed" or value.lower() == "yes":
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
