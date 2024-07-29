from flask import Flask, session
from datetime import datetime, date, timedelta
from flask_socketio import SocketIO, emit
from pubsub import pub

name = "penguins"
app = Flask(name)
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

def sendMessage(message):
    print('Function messageToUser received:')
    print('message =', message)
    socketio.emit('newmessage',{'message':message})

pub.subscribe(sendMessage, 'rootMessageSender')

def showUserMessage(msg):
    pub.sendMessage('rootMessageSender', message=msg)

def getCONum(userCONum):
    error = session.get('flash_errors')
    coIntCheck = False
    co1stCharCheck = False
    co2ndCharCheck = False
    # while coIntCheck != True or co1stCharCheck != True or co2ndCharCheck != True:
    # userCONum = input("Decomm CO: ")

    # check that user has input correct CO
    coCharsList = list(userCONum)

    if len(coCharsList) == 0:
        error = "please enter in a CO number"
        session['flash_errors'] = error
    else:
        if coCharsList[0].lower() == 'c':
            pass
        elif coCharsList[0].lower() != 'c':
            if error == None:
                error = "1st char is not 'c'."
                session['flash_errors'] = error
            else:
                error = str(error) + " " + "1st char is not 'c'."
                session['flash_errors'] = error

        if coCharsList[1].lower() == 'h':
            pass
        elif coCharsList[1].lower() != 'h':
            if error == None:
                error = "2nd char is not 'h'."
                session['flash_errors'] = error
            else:
                error = str(error) + " " + "2nd char is not 'h'."
                session['flash_errors'] = error

        try:
            coNums = int(userCONum[3:])
            # print(type(coNums))
            coIntCheck = isinstance(coNums, int)
            # print(intCheck)from datetime import datetime, date
        except:
            coIntCheck = False

        if coIntCheck == False:
            if error == None:
                error = "text chars found in the numbers portion of your CO"
                session['flash_errors'] = error
            else:
                error = str(error) + " " + "text chars found in the numbers portion of your CO"
                session['flash_errors'] = error


    # returns CO number in upper case.
    return userCONum.upper()


def getDecommCODate():
    CODate = str()
    # date format == "YYYY-mm-dd"
    # myDate = "2020-12-23"
    # dateObj = datetime.strptime(date, '%Y-%m-%d')
    # currentDate = dateObj
    currentDate = date.today()

    # day = int(str(currentDate).split('-')[2].split()[0])
    day = int(str(currentDate).split('-')[2])

    vmDeleteDateFifth = 5
    vmDeleteDateTwentyFifth = 25
    fatToAdd = 3
    addFatCurrentDate = day + fatToAdd

    if addFatCurrentDate < vmDeleteDateFifth:
        # within the same month
        CODay = "0" + str(vmDeleteDateFifth)
        month = currentDate.month
        if month < 10:
            month = "0" + str(month)
        year = year = currentDate.year
        CODate = str(year) + "-" + str(month) + "-" + CODay
    elif addFatCurrentDate >= vmDeleteDateFifth and addFatCurrentDate < vmDeleteDateTwentyFifth:
        # within the same month
        CODay = str(vmDeleteDateTwentyFifth)
        month = currentDate.month
        if month < 10:
            month = "0" + str(month)
        year = year = currentDate.year
        CODate = str(year) + "-" + str(month) + "-" + CODay
    elif addFatCurrentDate >= vmDeleteDateFifth and addFatCurrentDate >= vmDeleteDateTwentyFifth:
        # overlaps into next month
        CODay = "0" + str(vmDeleteDateFifth)
        monthsToAdd = 1
        month = currentDate.month - 1 + monthsToAdd
        year = currentDate.year + month // 12
        month = month % 12 + 1
        if month < 10:
            month = "0" + str(month)
        CODate = str(year) + "-" + str(month) + "-" + CODay

    return CODate


def getDecommVMDate():
    CODate = str()
    # date format == "YYYY-mm-dd"
    # myDate = "2020-12-23"
    # currentDate = dateObj
    currentDate = date.today()

    # get the day of the week.
    dayOfWeek = currentDate.weekday()

    # Friday (add 3 days, to get date to next Monday)
    if dayOfWeek == 5:
        daysToAdd = 3
    # Saturday (add 2 days, to get date to next Monday)
    elif dayOfWeek == 6:
        daysToAdd = 2
    # Any other day, add 1 day, for VM to be deleted the next day
    else:
        daysToAdd = 1

    # day = int(str(currentDate).split('-')[2].split()[0])
    day = currentDate.strftime("%d")
    month = currentDate.month
    year = year = currentDate.year
    
    vmDecommDate = currentDate + timedelta(days=daysToAdd)

    return vmDecommDate

def setBUSearchString():
    try:
        buNamesAccessList = session.get('bu_names_access_list')
    except:
        buNamesAccessList = list()

    if 'ALL' not in buNamesAccessList:
        if len(buNamesAccessList) == 1:
            buSearchString = buNamesAccessList[0]
        elif len(buNamesAccessList) > 1:
            i = 0
            for buName in buNamesAccessList:
                if i == 0:
                    buSearchString = "'" + buName + "'"
                if i > 0:
                    buSearchString = buSearchString + "," + "'" + buName + "'"

                i += 1
    else:
        buSearchString = 'ALL'

    return buSearchString
