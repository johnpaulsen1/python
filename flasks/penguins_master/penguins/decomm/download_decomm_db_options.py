from datetime import datetime
import os
from penguins.flaskdb import common_functions

dbName = "decommission"
dbTableName = "decommed_hosts"
report_file_name = "decomm"

def download_all():
    today = datetime.today().strftime('%Y-%m-%d')
    downloadReportFilePath = os.getcwd() + "/downloads/{}_report_{}.csv".format(report_file_name, today)

    dbQuery = "SELECT * FROM {};".format(dbTableName)
    decommReportResults = common_functions.dbQueryExecutor(dbName, dbQuery)

    if os.path.exists(downloadReportFilePath):
        os.remove(downloadReportFilePath)
    common_functions.createDecommHeaders(downloadReportFilePath)
    common_functions.writeDecommFile(downloadReportFilePath, decommReportResults)

    return downloadReportFilePath

def download_selected(selectResults):
    today = datetime.today().strftime('%Y-%m-%d')
    downloadReportFilePath = os.getcwd() + "/downloads/{}_report_{}.csv".format(report_file_name, today)
    decommReportResults = selectResults

    if os.path.exists(downloadReportFilePath):
        os.remove(downloadReportFilePath)

    print()
    print("creating file: '{}'.".format(downloadReportFilePath))
    try:
        common_functions.createDecommHeaders(downloadReportFilePath)
        common_functions.writeDecommFile(downloadReportFilePath, decommReportResults)
    except Exception as e:
        print("Exception:")
        print(e)

    return downloadReportFilePath
