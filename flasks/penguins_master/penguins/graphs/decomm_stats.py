import math
from flask import session
from datetime import datetime, timedelta
from penguins.other_utils import general
from penguins.flaskdb import common_functions
from penguins.ldap import get_ad_info

addExtraForMaximum = 0
dbName = "decommission"
dbTableName = "decommed_hosts"

def getDecommStatsByDate(time_from, time_to):
    decommSearchFromDate = time_from
    decommSearchFromDateList = decommSearchFromDate.split('-')
    fromDay = int(decommSearchFromDateList[0])
    fromMonth = int(decommSearchFromDateList[1])
    fromYear = int(decommSearchFromDateList[2])
    if len(str(fromDay)) == 1:
        fromDay = '0' + str(fromDay)
        fromDay = int(fromDay)

    decommSearchToDate = time_to
    decommSearchToDateList = decommSearchToDate.split('-')
    toDay = int(decommSearchToDateList[0])
    toMonth = int(decommSearchToDateList[1])
    toYear = int(decommSearchToDateList[2])
    if len(str(toDay)) == 1:
        toDay = '0' + str(toDay)
        toDay = int(toDay)

    searchColumn = "date_time_actioned"

    fromDate = datetime(fromYear, fromMonth, fromDay)
    toDate = datetime(toYear, toMonth, toDay)

    if fromDate > toDate:
        error = "FROM date CANNOT be GREATER than TO date, please try again..."
        session['flash_errors'] = error
        print(error)

    # add 1 day to 'toDate' so that Select query has a range to work with.
    # this is NEEDED for our implementation of datetime in our database.
    toDate = toDate + timedelta(days=1)
    fromDate = str(fromDate)[:10]
    toDate = str(toDate)[:10]
    selectQuery = "SELECT * FROM {} WHERE {} >= '{}' AND {} <= '{}';".format(
                    dbTableName,
                    searchColumn,
                    fromDate,
                    searchColumn,
                    toDate
    )
    session['search_decomm_db_from_date'] = fromDate
    session['search_decomm_db_to_date'] = toDate

    try:
        selectResults = common_functions.dbQueryExecutor(dbName, selectQuery)
        userDecommsDict = dict()

        for key, value in selectResults.items():
            result_list = value
            user = result_list[7]
            try:
                user_decomms_count = userDecommsDict.get(user)
                user_decomms_count += 1
                userDecommsDict[user] = user_decomms_count
            except:
                user_decomms_count = 1
                userDecommsDict[user] = user_decomms_count

        usersList = list()
        userNumDecommsList = list()

        for key in userDecommsDict.keys():
            usersList.append(key)

        updatedUsersList = list()
        for user in usersList:
            try:
                adUserName = get_ad_info.getUserName(user)
                user = "({}) {}".format(user, adUserName)
                updatedUsersList.append(user)

            except Exception as e:
                print("Exception caught: '{}'".format(str(e)))

        # add total column
        updatedUsersList.append("Total")

        for value in userDecommsDict.values():
            userNumDecommsList.append(value)

        # add total value
        total = sum(userNumDecommsList)
        userNumDecommsList.append(total)

        session['graph_labels'] = updatedUsersList
        session['graph_values'] = userNumDecommsList

        highestNum = max(userNumDecommsList)
        roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

        maxValue = roundedHighestNum + addExtraForMaximum
        # session['graph_max_value'] = maxValue
        session['graph_max_value'] = 0

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))


def getDecommStatsByUserOrCO(searchColumn, fieldToSearch):

    selectQuery = "SELECT * FROM {} WHERE {} IN ({});".format(
                    dbTableName,
                    searchColumn,
                    fieldToSearch
    )

    getTotalQuery = "SELECT COUNT(id) AS Total FROM {};".format(dbTableName)

    try:
        total = 0
        totalDict = common_functions.dbQueryExecutor(dbName, getTotalQuery)

        for value in totalDict.values():
            total = value

        selectResults = common_functions.dbQueryExecutor(dbName, selectQuery)
        userDecommsDict = dict()

        for key, value in selectResults.items():
            result_list = value
            user = result_list[7]
            try:
                user_decomms_count = userDecommsDict.get(user)
                user_decomms_count += 1
                userDecommsDict[user] = user_decomms_count
            except:
                user_decomms_count = 1
                userDecommsDict[user] = user_decomms_count

        usersList = list()
        userNumDecommsList = list()

        for key in userDecommsDict.keys():
            usersList.append(key)

        updatedUsersList = list()
        for user in usersList:
            try:
                adUserName = get_ad_info.getUserName(user)
                user = "({}) {}".format(user, adUserName)
                updatedUsersList.append(user)

            except Exception as e:
                print("Exception caught: '{}'".format(str(e)))

        # add total column
        updatedUsersList.append("Total")

        for value in userDecommsDict.values():
            userNumDecommsList.append(value)

        if total == 0:
            total = sum(userNumDecommsList)

        # add total value
        userNumDecommsList.append(total)

        session['graph_labels'] = updatedUsersList
        session['graph_values'] = userNumDecommsList

        highestNum = max(userNumDecommsList)
        roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

        maxValue = roundedHighestNum + addExtraForMaximum
        # session['graph_max_value'] = maxValue
        session['graph_max_value'] = 0

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))


def getAllDecommStats():

    selectQuery = "SELECT * FROM {};".format(
                    dbTableName
    )

    getTotalQuery = "SELECT COUNT(id) AS Total FROM {};".format(dbTableName)

    try:
        total = 0
        totalDict = common_functions.dbQueryExecutor(dbName, getTotalQuery)

        for value in totalDict.values():
            total = value

        selectResults = common_functions.dbQueryExecutor(dbName, selectQuery)
        userDecommsDict = dict()

        for key, value in selectResults.items():
            result_list = value
            user = result_list[7]
            try:
                user_decomms_count = userDecommsDict.get(user)
                user_decomms_count += 1
                userDecommsDict[user] = user_decomms_count
            except:
                user_decomms_count = 1
                userDecommsDict[user] = user_decomms_count

        usersList = list()
        userNumDecommsList = list()

        for key in userDecommsDict.keys():
            usersList.append(key)

        updatedUsersList = list()
        for user in usersList:
            try:
                adUserName = get_ad_info.getUserName(user)
                user = "({}) {}".format(user, adUserName)
                updatedUsersList.append(user)

            except Exception as e:
                print("Exception caught: '{}'".format(str(e)))

        # add total column
        updatedUsersList.append("Total")

        for value in userDecommsDict.values():
            userNumDecommsList.append(value)

        if total == 0:
            total = sum(userNumDecommsList)

        # add total value
        userNumDecommsList.append(total)

        session['graph_labels'] = updatedUsersList
        session['graph_values'] = userNumDecommsList

        highestNum = max(userNumDecommsList)
        roundedHighestNum = int(math.ceil(highestNum / 100.0)) * 100

        maxValue = roundedHighestNum + addExtraForMaximum
        # session['graph_max_value'] = maxValue
        session['graph_max_value'] = 0

    except Exception as e:
        print("unable to connect to DB: '{}' and execute query: '{}'".format(dbName, dbQuery))
        print("Exception caught: {}".format(str(e)))
