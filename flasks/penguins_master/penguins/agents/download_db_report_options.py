from datetime import datetime
import os
from penguins.flaskdb import common_functions

dbName = "tmc"

def download_all(agent, dbTableName):
    reportFileName = agent + '_agent_health_report'
    today = datetime.today().strftime('%Y-%m-%d')
    downloadReportFilePath = os.getcwd() + "/downloads/{}_{}.csv".format(reportFileName, today)

    dbQuery = "SELECT * FROM {};".format(dbTableName)
    report_results = common_functions.dbQueryExecutor(dbName, dbQuery)

    if os.path.exists(downloadReportFilePath):
        os.remove(downloadReportFilePath)
    common_functions.createAgentHealthHeaders(agent, downloadReportFilePath)
    common_functions.writeAgentHealthFile(agent, downloadReportFilePath, report_results)

    return downloadReportFilePath

def download_selected(agent, selectResults):
    reportFileName = agent + '_agent_health_report'
    today = datetime.today().strftime('%Y-%m-%d')
    downloadReportFilePath = os.getcwd() + "/downloads/{}_{}.csv".format(reportFileName, today)
    report_results = selectResults

    if os.path.exists(downloadReportFilePath):
        os.remove(downloadReportFilePath)
    common_functions.createAgentHealthHeaders(agent, downloadReportFilePath)
    common_functions.writeAgentHealthFile(agent, downloadReportFilePath, report_results)

    return downloadReportFilePath
