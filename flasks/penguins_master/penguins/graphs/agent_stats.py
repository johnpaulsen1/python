import math
from flask import session
from penguins.other_utils import general
from penguins.flaskdb import common_functions

def getAgentVersionStats():
    dbName = "tmc"
    dbTableName = "tmc_main"
    agents = [  'clamav_version', 'clamdb_version', 'splunk', 'tetration',
                'flexera', 'netbackup', 'checkmk', 'sudo', 'besagent', 'tmc',
                'ccs'
            ]
    queryType = "agent_count"

    try:
        agentVersionsDict = common_functions.dbMultiQueryExecutor(dbName, dbTableName, agents, queryType)
        session['agent_versions_installed_dict'] = agentVersionsDict

        maxValueDict = dict()

        for key, valueDict in agentVersionsDict.items():
            numAgentVersions = list()
            for value in valueDict.values():
                numAgentVersions.append(value)

            highestNum = max(numAgentVersions)
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
                addExtraForMaximum = 150
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
