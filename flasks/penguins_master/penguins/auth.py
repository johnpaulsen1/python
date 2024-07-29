import functools, ldap, io, ast, warnings, sys, json
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from ldap.controls import SimplePagedResultsControl
from cryptography.fernet import Fernet
import ssl
from pubsub import pub
import logging
from penguins.other_utils import general

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

bp = Blueprint('auth', __name__, url_prefix='/')
allowedADgroupsJsonFileName = "./penguins/static/auth/bu_allowed_ad_groups.json"
ldapServer = "ldaps://<ldap server>:636"
authServer = "ldaps://<auth server>:636"
ldapBase = "<ldap base>"
domain = "<domain>"
userDomain = "@"+domain
ldapServerDown = "Can't contact LDAP server"
flaskAcc = "<service account>"
flaskPwd = "not today...."
adSelfServiceSite = "https://<pwd reset site>"
pageSize = 2000
pageControl = SimplePagedResultsControl(True, size=pageSize, cookie='')

def encryptPwd(password, sleutel):
    encodePwd = password.encode()
    f = Fernet(sleutel)
    enctPwd = f.encrypt(encodePwd)
    return enctPwd

def decryptPwd(ePassword, sleutel):
    f = Fernet(sleutel)
    dectPwd = f.decrypt(ePassword).decode()
    return dectPwd

def init_ldap_con(this_dc):
    global error
    try:
        error = None
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        conn = ldap.initialize(this_dc)
        user = session.get('logged_in_user')
        encPwd = session.get('sessEncPwd')

        # set ldap protocol version & options for ldaps
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        conn.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
        conn.set_option(ldap.OPT_X_TLS_DEMAND, True)
        conn.set_option(ldap.OPT_DEBUG_LEVEL, 255)

        if userDomain not in user:
            user = user + userDomain

        # connect / bind to ldap server
        conn.simple_bind_s(user, decryptPwd(encPwd, session.get('sleutel')))

    except ldap.LDAPError as e:
        print(str(e))
        errorDict = ast.literal_eval(str(e))
        getADErrorInfo = errorDict['info'].split(", ")
        dataCode = str()
        ldapServerDown = str()
        logging.error("AD connection attempt for user: '{}' FAILED. See Exception below:".format(user))

        for item in getADErrorInfo:
            if "data" in item:
                dataCodeList = item.split(" ")
                dataCode = dataCodeList[1]
            if "comment" in item:
                errorMessageList = item.split(":")
                errorMessage = errorMessageList[1]

        if dataCode == "775":
            error = 'your account is locked...\n' + 'visit this site to unlock it.\n' + adSelfServiceSite
        elif dataCode == "52e":
            error = 'username / password mismatch'
        elif ldapServerDown in str(e):
            error = "AD server: " + this_dc + " not available"
        elif "In order to perform this operation a successful bind must be completed on the connection" in errorMessage:
            error = "You've lost connectivity to the LDAP server: " + this_dc  + ". Please log off and on again."
        else:
            error = 'something failed...\n' + str(e)
        
        if error:
            print(error)
            logging.error("Exception: '{}'.".format(error))

    except ldap.INVALID_CREDENTIALS:
        error = 'your credentials are invalid...'
        print(error)
        logging.error("AD connection attempt for user: '{}' FAILED. See Exception below:".format(user))
        logging.error("Exception: '{}'.".format(error))

    except ldap.NO_SUCH_OBJECT as e:
        error = "can't find user: " + user
        print(error)
        logging.error("AD connection attempt for user: '{}' FAILED. See Exception below:".format(user))
        logging.error("Exception: '{}'.".format(error))

    except ldap.SERVER_DOWN:
        error = "AD server: " + this_dc + " not available"
        print(error)
        logging.error("AD connection attempt for user: '{}' FAILED. See Exception below:".format(user))
        logging.error("Exception: '{}'.".format(error))

    except Exception as e:
        error = 'something failed...\n' + str(e)
        print(error)
        logging.error("AD connection attempt for user: '{}' FAILED. See Exception below:".format(user))
        logging.error("Exception: '{}'.".format(error))

    return conn

def check_user_access(masterUser, masterEpwd):
    global error, userADGroups
    # check if password is correct for user logging on...
    try:
        init_ldap_con(authServer)
    except Exception as e:
        error = "Exception caught: '{}'".format(str(e))
        print(error)
        logging.error("AD connection attempt for user: '{}' FAILED. See Exception below:".format(user))
        logging.error("Exception: '{}'.".format(error))

    try:
        userADGroups = list()
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        check_con = ldap.initialize(authServer)
        loggedInUser = session.get('logged_in_user')

        # set ldap protocol version & options for ldaps
        check_con.set_option(ldap.OPT_REFERRALS, 0)
        check_con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        check_con.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
        check_con.set_option(ldap.OPT_X_TLS_DEMAND, True)
        check_con.set_option(ldap.OPT_DEBUG_LEVEL, 255)

        if userDomain not in masterUser:
            masterUser = masterUser + userDomain

        # connect / bind to ldap server
        check_con.simple_bind_s(masterUser, decryptPwd(masterEpwd, session.get('sleutel')))

        query = '(sAMAccountName=%s)' % loggedInUser
        ldapSearchGroups(loggedInUser, query, check_con)
        # print(userADGroups)

    except ldap.LDAPError as e:
        errorDict = ast.literal_eval(str(e))
        getADErrorInfo = errorDict['info'].split(", ")
        dataCode = str()
        ldapServerDown = str()

        for item in getADErrorInfo:
            if "data" in item:
                dataCodeList = item.split(" ")
                dataCode = dataCodeList[1]
            if "comment" in item:
                errorMessageList = item.split(":")
                errorMessage = errorMessageList[1]

        if dataCode == "775":
            error = 'your account is locked...\n' + 'visit this site to unlock it.\n' + adSelfServiceSite
        elif dataCode == "52e":
            error = 'username / password mismatch' #+ str(e)
        elif ldapServerDown in str(e):
            error = "AD server: " + authServer + " not available"
        elif "In order to perform this operation a successful bind must be completed on the connection" in errorMessage:
            error = "You've lost connectivity to the LDAP server: " + authServer  + ". Please log off and on again."
        else:
            error = 'something failed...\n' + str(e)
        
        logging.error("AD connection attempt for master user: '{}' FAILED. See Exception below:".format(masterUser))
        logging.error("Exception: '{}'.".format(error))

    except ldap.INVALID_CREDENTIALS:
        error = 'your credentials are invalid...'
        logging.error("AD connection attempt for master user: '{}' FAILED. See Exception below:".format(masterUser))
        logging.error("Exception: '{}'.".format(error))

    except ldap.NO_SUCH_OBJECT as e:
        error = "can't find user: " + masterUser
        logging.error("AD connection attempt for master user: '{}' FAILED. See Exception below:".format(masterUser))
        logging.error("Exception: '{}'.".format(error))

    except ldap.SERVER_DOWN:
        error = "AD server: " + authServer + " not available"
        logging.error("AD connection attempt for master user: '{}' FAILED. See Exception below:".format(masterUser))
        logging.error("Exception: '{}'.".format(error))

    except Exception as e:
        error = 'something failed...\n' + str(e)
        logging.error("AD connection attempt for master user: '{}' FAILED. See Exception below:".format(masterUser))
        logging.error("Exception: '{}'.".format(error))

    return userADGroups;

# web route to display / redirect to the login page
@bp.route('/', methods=('GET', 'POST'))
@bp.route('/penguins', methods=('GET', 'POST'))
def home():
    session['already_logged_in'] = None
    # session['logged_in'] = False          # => used to get around user logged in checking
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if session.get('logged_in'):
        session['already_logged_in'] = "Hello " + session.get('logged_in_user') + " you're already logged on..."
        return redirect(url_for('main_options'))

# web route to display the login page
@bp.route('/penguins/login', methods=('GET', 'POST'))
def login():
    global error

    key = Fernet.generate_key()
    session['sleutel'] = key
    # reset variables when this method is called
    error = None
    accessError = None
    allowedAccess = False
    setAdminAccess = False
    setCMDBAccess = False
    setDecommDBAccess = False
    setMinimalAccess = False
    buNamesAccessList = list()
    foundErrorVisibility = "visibility_off"
    userInfoMessageVisibility = "visibility_off"
    twoFAMessage = "Please open the FNB App to Approve your login."
    session['already_logged_in'] = None

    if session.get('logged_in'):
        session['already_logged_in'] = "Hello " + session.get('logged_in_user') + " you're already logged on..."
        return redirect(url_for('main_options'))

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log in':
            # show user message that they must check FNB App for 2FA.
            userInfoMessageVisibility = "visibility_on"
            # flash(twoFAMessage)

            user = request.form['username']
            encPwd = encryptPwd(request.form['password'], session.get('sleutel'))
            session['logged_in_user'] = user
            session['sessEncPwd'] = encPwd
            flaskEpwd = encryptPwd(flaskPwd, session.get('sleutel'))
            allowedADgroupsJsonFile = open(allowedADgroupsJsonFileName, "r")
            allowedADgroupsJsonData = allowedADgroupsJsonFile.read()
            allowedADgroupsJsonObj = json.loads(allowedADgroupsJsonData)
            allowedADgroupsDict = allowedADgroupsJsonObj

            logging.info("user: '{}' is attempting to login.".format(user))

            # get logging in user's AD Groups
            loggedInUserADGroups = check_user_access(flaskAcc, flaskEpwd)

            if error is None:
                for dictKey, adGroups in allowedADgroupsDict.items():
                    if dictKey == "Admins":
                        infoMessage = "checking if logging in user is an admin..."
                        print(infoMessage)
                        logging.info(infoMessage)
                        for loggedInUserADGroup in loggedInUserADGroups:
                            if loggedInUserADGroup in adGroups:
                                setAdminAccess = True
                                break;
                    if setAdminAccess == True:
                        infoMessage = "admin access set for user: '{}'.".format(user)
                        print(infoMessage)
                        logging.info(infoMessage)
                        buNamesAccessList.append('ALL')
                        allowedAccess = True
                        break;

                    if dictKey == "CMDB":
                        infoMessage = "checking if logging in user is a memeber of the CMDB AD Group..."
                        print(infoMessage)
                        logging.info(infoMessage)
                        for loggedInUserADGroup in loggedInUserADGroups:
                            if loggedInUserADGroup in adGroups:
                                setCMDBAccess = True
                                break;
                    if setCMDBAccess == True:
                        infoMessage = "cmdb access set for user: '{}'.".format(user)
                        print(infoMessage)
                        logging.info(infoMessage)
                        buNamesAccessList.append('ALL')
                        allowedAccess = True
                        break;

                    if dictKey == "Decomms":
                        infoMessage = "checking if logging in user is a memeber of the Decomms DB AD Group..."
                        print(infoMessage)
                        logging.info(infoMessage)
                        for loggedInUserADGroup in loggedInUserADGroups:
                            if loggedInUserADGroup in adGroups:
                                setDecommDBAccess = True
                                break;
                    if setDecommDBAccess == True:
                        infoMessage = "decomm db access set for user: '{}'.".format(user)
                        print(infoMessage)
                        logging.info(infoMessage)
                        allowedAccess = True

                    if setAdminAccess == False and (setCMDBAccess == False or setDecommDBAccess == False):
                        for loggedInUserADGroup in loggedInUserADGroups:
                            if loggedInUserADGroup in adGroups:
                                if dictKey != "Admins":
                                    buNamesAccessList.append(dictKey)
                                    break;

                if setAdminAccess == False and (setCMDBAccess == False or setDecommDBAccess == False) and len(buNamesAccessList) == 0:
                    infoMessage = "setting minimal access for user: '{}'.".format(user)
                    print(infoMessage)
                    logging.info(infoMessage)
                    setMinimalAccess = True
                    allowedAccess = True
                elif setAdminAccess == False and (setCMDBAccess == False or setDecommDBAccess == False) and len(buNamesAccessList) > 0:
                    infoMessage = "setting tmc and cmdb access for user: '{}'.".format(user)
                    print(infoMessage)
                    logging.info(infoMessage)
                    setCMDBAccess = True
                    allowedAccess = True

                # set what the user is allowed to see in the menu
                if allowedAccess:
                    session['bu_names_access_list'] = buNamesAccessList
                    session['admin_access'] = setAdminAccess
                    session['cmdb_access'] = setCMDBAccess
                    session['decommdb_access'] = setDecommDBAccess
                    session['minimal_access'] = setMinimalAccess
                else:
                    accessError = "permission denied for user: " + user + ". SORRY... \n " + \
                    "Please request access from the admins."


        if error is None and allowedAccess:
            foundErrorVisibility = "visibility_off"
            session['logged_in'] = True
            session['logged_in_user'] = user
            liveMessage = "user: '{}' successfully logged in.".format(user)
            print(liveMessage)
            logging.info(liveMessage)
            print()
            general.showUserMessage(liveMessage)
            return redirect(url_for('main_options'))
        elif error != None:
            foundErrorVisibility = "visibility_on"
            flash(error)
        elif accessError != None:
            foundErrorVisibility = "visibility_on"
            flash(accessError)
            print(accessError)
            logging.warning(accessError)

    return render_template('auth/login.html',
                            setErrorVisibility = foundErrorVisibility,
                            userInfoMessageVisibility = userInfoMessageVisibility,
                            userMessage = twoFAMessage
                            )


# ldap query tool - main page
@bp.route('/penguins/ldap', methods=('GET', 'POST'))
def ldap_main():

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('main_options'))
        elif request.form['submit_button'] == "User's details":
            return redirect(url_for('ldap_user_details'))
        elif request.form['submit_button'] == "Groups a User belongs to":
            return redirect(url_for('ldap_users_group_membership'))
        elif request.form['submit_button'] == "Members of a Group":
            return redirect(url_for('ldap_group_members'))
        elif request.form['submit_button'] == "Check Unix Group":
            return redirect(url_for('ldap_unix_groups'))
        elif request.form['submit_button'] == "User locked out?":
            return redirect(url_for('ldap_user_lock_status'))

    return render_template('ldap_query/options.html')

@bp.route('/penguins/ldap/user_details', methods=('GET', 'POST'))
def ldap_user_details():
    global displayListValues, displayListStatics, visibility, searchUser, error

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # reset variables when this method is called
    error = None
    displayListValues = []
    displayListStatics = []
    visibility = "visibility_off"
    searchUser = ""

    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('ldap_main'))
        elif request.form['submit_button'] == 'Search':
            try:
                uid = request.form['username']
                try:
                    firstCharUID = int(uid[0])
                except:
                    firstCharUID = str(uid[0])
                testChar = isinstance(firstCharUID, str)

                if testChar:
                    if " " in uid and "," not in uid:
                        error = "usage: firstname, lastname OR input a username"
                    elif "," in uid or " " in uid:
                        # set search query based on user input
                        query = '(cn=%s)' % uid
                        ldapSearchUser(uid, query, init_ldap_con(ldapServer))
                    else:
                        # set search query based on user input
                        digitsOnlyUID = ''.join(filter(lambda i: i.isdigit(), uid))
                        wildCardUID = "*" + uid + "*"
                        query = '(sAMAccountName=%s)' % uid
                        # query = '(sAMAccountName=%s)' % wildCardUID
                        ldapSearchUser(uid, query, init_ldap_con(ldapServer))
                else:
                    digitsOnlyUID = ''.join(filter(lambda i: i.isdigit(), uid))
                    wildCardUID = "*" + uid
                    query = '(sAMAccountName=%s)' % wildCardUID
                    ldapSearchUser(uid, query, init_ldap_con(ldapServer))

            except Exception as e:
                error = 'Exception caught:\n' + str(e)
                print(error)
                logging.info(error)

            if error is None:
                return render_template('ldap_query/user_details.html',
                listsOfListValues = displayListValues, listStatics = displayListStatics,
                setVisibility = visibility, foundUser = searchUser)
            elif error != None:
                flash(error)

    return render_template('ldap_query/user_details.html', setVisibility = visibility)

# method for searching and returning info for a specified AD user
def ldapSearchUser(uid, query, conn):
    global displayListValues, displayListStatics, visibility, searchUser, error
    user = session.get('logged_in_user')

    logging.info("user: '{}' is attempting to query AD, searching for user: '{}'".format(user, uid))

    try:
        error = None
        displayListStatics = ['Title:', 'Full Name:', 'Employee No:', 'Job Title:',
        'Join Date:', 'Company Code:', 'Cost Centre:', 'Manager:', 'Email Address:',
        'Tel Number:', 'Cell Number:', 'Default Shell:', 'Default Home Dir:',
        'Unix Group:', 'AD Location:']
        i = 0
        # search ldap server
        resultList = conn.search_s(ldapBase, ldap.SCOPE_SUBTREE, query)

        for listItem in resultList[:-1]:
            workingUserList = list()
            resultTup = resultList[i]
            i = i + 1
            userDetailsDict = resultTup[1]

            # if statements below check if specic fields of the user are defined.
            # if they are not defined, varible set to empty.
            if 'personalTitle' in userDetailsDict.keys():
                userTitle = userDetailsDict["personalTitle"][0].decode()
            else:
                userTitle = "N/A"
            workingUserList.append(userTitle)

            if 'displayName' in userDetailsDict.keys():
                userFullName = userDetailsDict["displayName"][0].decode()
            else:
                userFullName = "N/A"
            workingUserList.append(userFullName)

            # if 'employeeID' in userDetailsDict.keys():
            if 'sAMAccountName' in userDetailsDict.keys():
                # userEmpID = userDetailsDict["employeeID"][0].decode()
                userEmpID = userDetailsDict["sAMAccountName"][0].decode()
            else:
                userEmpID = "N/A"
            workingUserList.append(userEmpID)

            if 'title' in userDetailsDict.keys():
                userJobTitle = userDetailsDict["title"][0].decode()
            else:
                userJobTitle = "N/A"
            workingUserList.append(userJobTitle)

            if 'whenCreated' in userDetailsDict.keys():
                userJoinDateList = userDetailsDict["whenCreated"][0].decode().split(".")
                userJoinDate = userJoinDateList[0]
                userJoinYear = userJoinDate[:4]
                userJoinMonth = userJoinDate[4:6]
                userJoinDay = userJoinDate[6:8]
                userJoinDisplayDate = (userJoinDay + "/" + userJoinMonth + "/" + userJoinYear)
            else:
                userJoinDisplayDate = "N/A"
            workingUserList.append(userJoinDisplayDate)

            if 'physicalDeliveryOfficeName' in userDetailsDict.keys():
                userCompCode = userDetailsDict["physicalDeliveryOfficeName"][0].decode()
            else:
                userCompCode = "N/A"
            workingUserList.append(userCompCode)

            if 'businessCategory' in userDetailsDict.keys():
                userCostCenter = userDetailsDict["businessCategory"][0].decode()
            else:
                userCostCenter = "N/A"
            workingUserList.append(userCostCenter)

            if 'manager' in userDetailsDict.keys():
                userManagerList = userDetailsDict["manager"][0].decode().split(",")
                userManager = (userManagerList[0] + userManagerList[1]).replace("CN=","").replace("\\",",")
            else:
                userManager = "N/A"
            workingUserList.append(userManager)

            if 'mail' in userDetailsDict.keys():
                userEmail = userDetailsDict["mail"][0].decode()
            else:
                userEmail = "N/A"
            workingUserList.append(userEmail)

            if 'telephoneNumber' in userDetailsDict.keys():
                userTelNumber = userDetailsDict["telephoneNumber"][0].decode()
            else:
                userTelNumber = "N/A"
            workingUserList.append(userTelNumber)

            if 'mobile' in userDetailsDict.keys():
                userMobNumber = userDetailsDict["mobile"][0].decode()
            else:
                userMobNumber = "N/A"
            workingUserList.append(userMobNumber)

            if 'loginShell' in userDetailsDict.keys():
                userLoginShell = userDetailsDict["loginShell"][0].decode()
            else:
                userLoginShell = "N/A"
            workingUserList.append(userLoginShell)

            if 'unixHomeDirectory' in userDetailsDict.keys():
                userHomeDir = userDetailsDict["unixHomeDirectory"][0].decode()
            else:
                userHomeDir = "N/A"
            workingUserList.append(userHomeDir)

            # set query for unix account search
            firstCharEmpID = userEmpID[0].lower()

            if 'f' not in firstCharEmpID:
                queryUnix = '(sAMAccountName=unix-f%s)' % userEmpID
                getUnixAcc = True
            elif 'f' in firstCharEmpID:
                queryUnix = '(sAMAccountName=unix-%s)' % userEmpID
                getUnixAcc = True
            else:
                getUnixAcc = False

            if getUnixAcc:
                # check if user has a unix account
                resultListUnix = conn.search_s(ldapBase, ldap.SCOPE_SUBTREE, queryUnix)
                resultTupUnix = resultListUnix[0]
                userDetailsDictUnix = resultTupUnix[1]

                if resultTupUnix[0] is not None:
                    if 'cn' in userDetailsDictUnix.keys():
                        unixAccount = userDetailsDictUnix["cn"][0].decode()
                    else:
                        unixAccount = "N/A"
                else:
                    unixAccount = "N/A"
            else:
                unixAccount = "N/A"
            workingUserList.append(unixAccount)

            if resultTup:
                dnList = resultTup[0].split("=")
                replaceStr = "CN=" + dnList[1].replace(",OU","") + ","
                userDistinguishedName = resultTup[0].replace(replaceStr,"")
            else:
                userDistinguishedName = "N/A"
            workingUserList.append(userDistinguishedName)

            # adding elements to displayListValues
            displayListValues.append(workingUserList)

    except ldap.LDAPError as e:
        errorDict = ast.literal_eval(str(e))
        getADErrorInfo = errorDict['info'].split(", ")

        for item in getADErrorInfo:
            if "data" in item:
                dataCodeList = item.split(" ")
                dataCode = dataCodeList[1]
            if "comment" in item:
                errorMessageList = item.split(":")
                errorMessage = errorMessageList[1]

        if dataCode == "775":
            error = 'your account is locked...\n' + 'visit this site to unlock it.\n' + adSelfServiceSite
        elif dataCode == "52e":
            error = 'username / password mismatch' #+ str(e)
        elif ldapServerDown in str(e):
            error = "AD server: " + ldapServer + " not available"
        elif "In order to perform this operation a successful bind must be completed on the connection" in errorMessage:
            error = "You've lost connectivity to the LDAP server: " + ldapServer  + ". Please log off and on again."
        else:
            error = 'something failed...\n' + str(e)
        
        logging.error("AD search attempt FAILED. See Exception below:")
        logging.error("Exception: '{}'.".format(error))

    except ldap.NO_SUCH_OBJECT as e:
        error = "can't find user: " + uid
        logging.error("AD search attempt FAILED. See Exception below:")
        logging.error("Exception: '{}'.".format(error))

    except ldap.SERVER_DOWN:
        error = "AD server: " + ldapServer + " not available"
        logging.error("AD search attempt FAILED. See Exception below:")
        logging.error("Exception: '{}'.".format(error))

    except Exception as e:
        capturedError = str(e)

        if uid == "":
            error = "No username entered... Please try again."
        elif "'list' object has no attribute 'keys'" in capturedError and uid != "":
            error = "can't find user: " + uid
        else:
            error = 'Exception caught:\n' + str(e)

        logging.error("AD search attempt FAILED. See Exception below:")
        logging.error("Exception: '{}'.".format(error))

    if error is None:
        for dispList in displayListValues:
            print(dispList)

        visibility = "visibility_on"
        searchUser = uid

    if conn:
        # unbind connection to ldap server
        conn.unbind()

# web route to query a users group membership
@bp.route('/penguins/ldap/users_group_membership', methods=('GET', 'POST'))
def ldap_users_group_membership():
    global displayListValues, visibility, searchUser, displayUserADLocation, error
    user = session.get('logged_in_user')

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # reset variables when this method is called
    error = None
    displayListValues = []
    visibility = "visibility_off"
    searchUser = ""
    displayUserADLocation = ""

    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('ldap_main'))

        elif request.form['submit_button'] == 'Search':
            try:
                uid = request.form['username']
                logging.info("user: '{}' is attempting to query AD, searching for user's: '{}' group membership".format(user, uid))

                if " " in uid and "," not in uid:
                    error = "usage: firstname, lastname OR input a username"
                    logging.error(error)
                elif "," in uid or " " in uid:
                    # set search query based on user input
                    query = '(cn=%s)' % uid
                    ldapSearchGroups(uid, query, init_ldap_con(ldapServer))
                else:
                    # set search query based on user input
                    digitsOnlyUID = ''.join(filter(lambda i: i.isdigit(), uid))
                    wildCardUID = "*" + uid + "*"
                    query = '(sAMAccountName=%s)' % uid
                    # query = '(sAMAccountName=%s)' % wildCardUID
                    ldapSearchGroups(uid, query, init_ldap_con(ldapServer))

            except Exception as e:
                error = 'Exception caught:\n' + str(e)
                logging.error("AD search attempt FAILED. See Exception below:")
                logging.error("Exception: '{}'.".format(error))

            if error is None:
                return render_template('ldap_query/users_group_membership.html',
                listValues = displayListValues, setVisibility = visibility,
                foundUser = searchUser, uidADLoc = displayUserADLocation)
            elif error != None:
                flash(error)

    return render_template('ldap_query/users_group_membership.html', setVisibility = visibility)

# method for searching and returning the AD groups a user belongs to
def ldapSearchGroups(uid, query, conn):
    global displayListValues, visibility, searchUser, displayUserADLocation, error, userADGroups
    try:
        groupNameList = []
        # search ldap server
        resultList = conn.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['memberOf',])
        resultTup = resultList[0]
        userDetails = resultTup[0]
        userGroupsDict = resultTup[1]

        # uid AD Location
        resultListUid = conn.search_s(ldapBase, ldap.SCOPE_SUBTREE, query)
        resultTupUid = resultListUid[0]
        userDetailsDict = resultTupUid[1]

        for dictKey, value in userGroupsDict.items():
            for item in value:
                decoded_item = item.decode()
                group = decoded_item.split(",")
                # group value: ['CN=xxx', 'OU=xxx', 'DC=xxx', 'DC=xx', 'DC=xx']
                # [0] for first item in the list "group"
                groupName = group[0].split("=")
                # groupName value: ['CN', '<AD group name>']
                # [1] for second item in list "groupName"
                groupNameList.append(groupName[1])

        if resultTup:
            dnList = resultTup[0].split("=")
            replaceStr = "CN=" + dnList[1].replace(",OU","") + ","
            userDistinguishedName = resultTup[0].replace(replaceStr,"")
        else:
            userDistinguishedName = "N/A"

    except ldap.LDAPError as e:
        errorDict = ast.literal_eval(str(e))
        getADErrorInfo = errorDict['info'].split(", ")

        for item in getADErrorInfo:
            if "data" in item:
                dataCodeList = item.split(" ")
                dataCode = dataCodeList[1]
            if "comment" in item:
                errorMessageList = item.split(":")
                errorMessage = errorMessageList[1]

        if dataCode == "775":
            error = 'your account is locked...\n' + 'visit this site to unlock it.\n' + adSelfServiceSite
        elif dataCode == "52e":
            error = 'username / password mismatch' #+ str(e)
        elif ldapServerDown in str(e):
            error = "AD server: " + ldapServer + " not available"
        elif "In order to perform this operation a successful bind must be completed on the connection" in errorMessage:
            error = "You've lost connectivity to the LDAP server: " + ldapServer  + ". Please log off and on again."
        else:
            error = 'something failed...\n' + str(e)

    except ldap.NO_SUCH_OBJECT as e:
        error = "can't find user: " + uid

    except ldap.SERVER_DOWN:
        error = "AD server: " + ldapServer + " not available"

    except Exception as e:
        capturedError = str(e)

        if uid == "":
            error = "No username entered... Please try again."
        elif "'list' object has no attribute 'items'" in capturedError and uid != "":
            error = "can't find user: " + uid
        else:
            error = 'something failed...\n' + str(e)

    if error is None:
        visibility = "visibility_on"
        searchUser = uid
        displayListValues = groupNameList
        userADGroups = groupNameList
        displayUserADLocation = userDistinguishedName

    if conn:
        # unbind connection to ldap server
        conn.unbind()

# web route to query users membership to a specific AD group
@bp.route('/penguins/ldap/group_members', methods=('GET', 'POST'))
def ldap_group_members():
    global displayListValues, visibility, searchGroup, displayGroupADLocation, error

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # reset variables when this method is called
    error = None
    displayListValues = []
    visibility = "visibility_off"
    searchGroup = ""
    displayGroupADLocation = ""

    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('ldap_main'))
        elif request.form['submit_button'] == 'Search':
            try:
                gid = request.form['groupname']
                # set search query
                query = '(cn=%s)' % gid
                ldapSearchGroupMembership(gid, query, init_ldap_con(ldapServer))

            except Exception as e:
                error = 'something failed...\n' + str(e)

            if error is None:
                return render_template('ldap_query/group_members.html',
                listValues = displayListValues, setVisibility = visibility,
                foundGroup = searchGroup, gidADLoc = displayGroupADLocation)
            elif error != None:
                flash(error)

    return render_template('ldap_query/group_members.html', setVisibility = visibility)

# method for checking whose members of a certain group
def ldapSearchGroupMembership(gid, query, conn):
    global displayListValues, visibility, searchGroup, displayGroupADLocation, error
    try:
        error = None
        memberNameList = []
        # search ldap server
        resultList = conn.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['member',])
        resultTup = resultList[0]
        resultDict = resultTup[1]

        # gid AD Location
        resultListGid = conn.search_s(ldapBase, ldap.SCOPE_SUBTREE, query)
        resultTupGid = resultListGid[0]
        groupDetailsDict = resultTupGid[1]

        for dictKey, value in resultDict.items():
            for item in value:
                decoded_item = item.decode()
                member = decoded_item.split(",")
                # member value: ['CN=Paulsen\\', ' John', 'OU=DomainUsers', 'DC=fnb', 'DC=co', 'DC=za']
                # [0] for last name , [1] for fist name in the list "member"
                fullMemberName = (member[0] + member[1])
                memberName = fullMemberName.split("=")
                # memberName value: ['CN', 'Paulsen\\ John']
                # [1] for second item in list "memberName"
                memberNameList.append(memberName[1].replace("OU","").replace("\\",","))

        if resultTup:
            dnList = resultTup[0].split("=")
            replaceStr = "CN=" + dnList[1].replace(",OU","") + ","
            groupDistinguishedName = resultTup[0].replace(replaceStr,"")
        else:
            groupDistinguishedName = "N/A"

    except ldap.LDAPError as e:
        errorDict = ast.literal_eval(str(e))
        getADErrorInfo = errorDict['info'].split(", ")

        for item in getADErrorInfo:
            if "data" in item:
                dataCodeList = item.split(" ")
                dataCode = dataCodeList[1]
            if "comment" in item:
                errorMessageList = item.split(":")
                errorMessage = errorMessageList[1]

        if dataCode == "775":
            error = 'your account is locked...\n' + 'visit this site to unlock it.\n' + adSelfServiceSite
        elif dataCode == "52e":
            error = 'username / password mismatch' #+ str(e)
        elif ldapServerDown in str(e):
            error = "AD server: " + ldapServer + " not available"
        elif "In order to perform this operation a successful bind must be completed on the connection" in errorMessage:
            error = "You've lost connectivity to the LDAP server: " + ldapServer  + ". Please log off and on again."
        else:
            error = 'something failed...\n' + str(e)

    except ldap.NO_SUCH_OBJECT as e:
        error = "can't find group: " + gid

    except ldap.SERVER_DOWN:
        error = "AD server: " + ldapServer + " not available"

    except Exception as e:
        capturedError = str(e)
        if gid == "":
            error = "No username entered... Please try again."
        elif "'list' object has no attribute 'items'" in capturedError and gid != "":
            error = "can't find group: " + gid
        else:
            error = 'something failed...\n' + str(e)

    if error is None:
        visibility = "visibility_on"
        searchGroup = gid
        displayListValues = memberNameList
        displayGroupADLocation = groupDistinguishedName

    if conn:
        # unbind connection to ldap server
        conn.unbind()

# web route to query unix accounts
@bp.route('/penguins/ldap/unix_groups', methods=('GET', 'POST'))
def ldap_unix_groups():
    global displayListValues, displayListUnixAccADLocation, visibility, searchUnixAcc, displayHeading, error

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # reset variables when this method is called
    error = None
    displayListValues = []
    displayListAllValues = []
    displayListUnixAccADLocation = []
    visibility = "visibility_off"
    visibilityAllUnix = "visibility_off"
    searchUnixAcc = ""
    displayHeading = ""

    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('ldap_main'))
        elif request.form['submit_button'] == 'All Unix Accounts':
            try:
                query = '(cn=unix-*)'
                ldapSeachAllUnixAcc(query, init_ldap_con(ldapServer))

            except Exception as e:
                error = 'something failed...\n' + str(e)

            if error is None:
                return render_template('ldap_query/unix_groups.html',
                listValues = displayListValues, listDN = displayListUnixAccADLocation,
                setVisibility = visibility, foundUser = searchUnixAcc,
                resultHeading = displayHeading)
            elif error != None:
                flash(error)

        elif request.form['submit_button'] == 'Search':
            try:
                uid = request.form['username']
                # set search query
                if " " in uid and "," not in uid:
                    error = "usage: firstname, lastname OR input a username"
                elif "," in uid or " " in uid:
                    # set search query based on user input
                    query = '(cn=%s)' % uid
                    ldapSeachUnixAcc(uid, query, init_ldap_con(ldapServer))
                elif '*' in uid:
                    query = '(cn=%s)' % uid
                    ldapSeachUnixAcc(uid, query, init_ldap_con(ldapServer))
                elif '*' not in uid and 'unix' not in uid:
                    query = '(cn=unix-*%s*)' % uid
                    ldapSeachUnixAcc(uid, query, init_ldap_con(ldapServer))
                elif '*' not in uid and 'unix' in uid:
                    query = '(cn=*%s*)' % uid
                    ldapSeachUnixAcc(uid, query, init_ldap_con(ldapServer))

            except Exception as e:
                if uid == "":
                    error = "No username entered... Please try again."
                else:
                    error = 'something failed...\n' + str(e)

            if error is None:
                return render_template('ldap_query/unix_groups.html',
                listValues = displayListValues, listDN = displayListUnixAccADLocation,
                setVisibility = visibility, foundUser = searchUnixAcc,
                resultHeading = displayHeading)
            elif error != None:
                flash(error)

    return render_template('ldap_query/unix_groups.html', setVisibility = visibility,
    setVisibilityAllUnix = visibilityAllUnix)

# method for returning all unix accounts
def ldapSeachAllUnixAcc(query, conn):
    global displayListValues, displayListUnixAccADLocation, visibility, displayHeading, error
    try:
        error = None
        msgid = conn.search_ext(ldapBase, ldap.SCOPE_SUBTREE, query, serverctrls=[pageControl])
        rtype, rdata, rmsgid, serverctrls = conn.result3(msgid)
        unixAccList = []
        unixAccDNList = []

        for dn, attrs in rdata:
            if dn is not None:
                dnList = dn.split(',')
                unixAcc = dnList[0].split('=')[1]
                uid = unixAcc.split('-')[1]
                unixAccList.append(unixAcc)
                replaceStr = "CN=" + unixAcc + ","

                if isinstance(attrs, dict):
                    unixAccDN = attrs['distinguishedName'][0].decode().replace(replaceStr,"")
                    unixAccDNList.append(unixAccDN)
                else:
                    unixAccDNList.append("N/A")

            elif dn is None and uid not in str(unixAccList):
                unixAcc = uid + " does not have a unix account"
                unixAccList.append(unixAcc)
                unixAccDNList.append("N/A")

    except ldap.LDAPError as e:
        errorDict = ast.literal_eval(str(e))
        getADErrorInfo = errorDict['info'].split(", ")

        for item in getADErrorInfo:
            if "data" in item:
                dataCodeList = item.split(" ")
                dataCode = dataCodeList[1]
            if "comment" in item:
                errorMessageList = item.split(":")
                errorMessage = errorMessageList[1]

        if dataCode == "775":
            error = 'your account is locked...\n' + 'visit this site to unlock it.\n' + adSelfServiceSite
        elif dataCode == "52e":
            error = 'username / password mismatch' #+ str(e)
        elif ldapServerDown in str(e):
            error = "AD server: " + ldapServer + " not available"
        elif "In order to perform this operation a successful bind must be completed on the connection" in errorMessage:
            error = "You've lost connectivity to the LDAP server: " + ldapServer  + ". Please log off and on again."
        else:
            error = 'something failed...\n' + str(e)

    except ldap.NO_SUCH_OBJECT as e:
        error = "can't find unix account/s"

    except ldap.SERVER_DOWN:
        error = "AD server: " + ldapServer + " not available"

    except Exception as e:
        capturedError = str(e)
        if "'list' object has no attribute 'items'" in capturedError:
            error = "can't find unix account/s"
        else:
            error = 'something failed...\n' + str(e)

    if error is None:
        # visibilityAllUnix = "visibility_on_all_unix"
        visibility = "visibility_on"
        # displayListAllValues = unixAccList
        displayListValues = unixAccList
        displayListUnixAccADLocation = unixAccDNList
        displayHeading = "See ALL 'unix-' groups below:"

    if conn:
        # unbind connection to ldap server
        conn.unbind()

# method for returning all unix accounts
def ldapSeachUnixAcc(uid, query, conn):
    global displayListValues, displayListUnixAccADLocation, visibility, searchUnixAcc, displayHeading, error
    try:
        error = None
        searchUnixAcc = uid

        if "," in uid or " " in uid:
            resultList = conn.search_s(ldapBase, ldap.SCOPE_SUBTREE, query)
            resultTup = resultList[0]
            userDetailsDict = resultTup[1]

            if 'employeeID' in userDetailsDict.keys():
                userEmpID = userDetailsDict["employeeID"][0].decode()

                # set query for unix account search
                if 'f' not in userEmpID:
                    query = '(cn=unix-f%s)' % userEmpID
                    uid = "f" + userEmpID
                elif 'f' in userEmpID:
                    query = '(cn=unix-%s)' % userEmpID
                    uid = userEmpID

        msgid = conn.search_ext(ldapBase, ldap.SCOPE_SUBTREE, query, serverctrls=[pageControl])
        rtype, rdata, rmsgid, serverctrls = conn.result3(msgid)
        unixAccList = []
        unixAccDNList = []

        for dn, attrs in rdata:

            if dn is not None:
                dnList = dn.split(',')
                unixAcc = dnList[0].split('=')[1]
                unixAccList.append(unixAcc)
                replaceStr = "CN=" + unixAcc + ","

                if isinstance(attrs, dict):
                    unixAccDN = attrs['distinguishedName'][0].decode().replace(replaceStr,"")
                    unixAccDNList.append(unixAccDN)
                else:
                    unixAccDNList.append("N/A")

            elif dn is None and uid not in str(unixAccList):
                unixAcc = uid + " does not have a unix account"
                unixAccList.append(unixAcc)
                unixAccDNList.append("N/A")

    except ldap.LDAPError as e:
        errorDict = ast.literal_eval(str(e))
        getADErrorInfo = errorDict['info'].split(", ")

        for item in getADErrorInfo:
            if "data" in item:
                dataCodeList = item.split(" ")
                dataCode = dataCodeList[1]
            if "comment" in item:
                errorMessageList = item.split(":")
                errorMessage = errorMessageList[1]

        if dataCode == "775":
            error = 'your account is locked...\n' + 'visit this site to unlock it.\n' + adSelfServiceSite
        elif dataCode == "52e":
            error = 'username / password mismatch' #+ str(e)
        elif ldapServerDown in str(e):
            error = "AD server: " + ldapServer + " not available"
        elif "In order to perform this operation a successful bind must be completed on the connection" in errorMessage:
            error = "You've lost connectivity to the LDAP server: " + ldapServer  + ". Please log off and on again."
        else:
            error = 'something failed...\n' + str(e)

    except ldap.NO_SUCH_OBJECT as e:
        error = "can't find unix account for: " + uid

    except ldap.SERVER_DOWN:
        error = "AD server: " + ldapServer + " not available"

    except Exception as e:
        capturedError = str(e)
        if uid == "":
            error = "No username entered... Please try again."
        elif "'list' object has no attribute 'keys'" in capturedError and uid != "":
            error = "can't find a unix account for user: " + uid
        else:
            error = 'something failed...\n' + str(e)

    if error is None:
        visibility = "visibility_on"
        displayListValues = unixAccList
        displayListUnixAccADLocation = unixAccDNList
        displayHeading = "See search results below for:"

    if conn:
        # unbind connection to ldap server
        conn.unbind()

# web route to check if a user account is locked out
@bp.route('/penguins/ldap/check_user_lock_status', methods=('GET', 'POST'))
def ldap_user_lock_status():
    global displayLockStatus, visibility, searchUser, error

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # reset variables when this method is called
    error = None
    displayLockStatus = ""
    visibility = "visibility_off"
    searchUser = ""

    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form['submit_button'] == 'Log Out':
            logout()
            return redirect(url_for('login'))
        elif request.form['submit_button'] == 'Back':
            return redirect(url_for('ldap_main'))

        elif request.form['submit_button'] == 'Search':
            try:
                uid = request.form['username']
                if " " in uid and "," not in uid:
                    error = "usage: firstname, lastname OR input a username"
                elif "," in uid or " " in uid:
                    # set search query based on user input
                    query = '(cn=%s)' % uid
                    ldapSearchUserLock(uid, query, init_ldap_con(ldapServer))
                else:
                    # set search query based on user input
                    digitsOnlyUID = ''.join(filter(lambda i: i.isdigit(), uid))
                    wildCardUID = "*" + uid + "*"
                    query = '(sAMAccountName=%s)' % uid
                    # query = '(sAMAccountName=%s)' % wildCardUID
                    ldapSearchUserLock(uid, query, init_ldap_con(ldapServer))

            except Exception as e:
                if uid == "":
                    error = "No username entered... Please try again."
                else:
                    error = 'something failed...\n' + str(e)

            if error is None:
                if "is NOT locked" in displayLockStatus:
                    setUserLockDisplay = "user_is_not_locked"
                elif "IS LOCKED" in displayLockStatus:
                    setUserLockDisplay = "user_is_locked"
                elif "determining lock status" in displayLockStatus:
                    setUserLockDisplay = "user_lock_status_undetermined"

                return render_template('ldap_query/user_lock_status.html',
                lockStatus = displayLockStatus, setVisibility = visibility,
                foundUser = searchUser, userLockDisplay = setUserLockDisplay)

            elif error != None:
                flash(error)

    return render_template('ldap_query/user_lock_status.html', setVisibility = visibility)

# method for checking if a users account is locked out.
def ldapSearchUserLock(uid, query, conn):
    global displayLockStatus, visibility, searchUser, error
    try:
        error = None
        # search ldap server
        resultAllList = conn.search_s(ldapBase, ldap.SCOPE_SUBTREE, query)
        resultLockTimeList = conn.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['lockoutTime',])
        resultLockDurationList = conn.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['lockoutDuration',])
        resultLockTimeTup = resultLockTimeList[0]
        userLockTimeDetails = resultLockTimeTup[0]
        userLockTimeDict = resultLockTimeTup[1]

        for dictKey, value in userLockTimeDict.items():
            userLockTime = int(value[0].decode())
            if userLockTime == 0:
                userLocktatus = (uid + ' is NOT locked')
            elif userLockTime != 0:
                userLocktatus = (uid + ' IS LOCKED')
            else:
                userLocktatus = ("determining lock status of: " + uid + " failed...")

    except ldap.LDAPError as e:
        errorDict = ast.literal_eval(str(e))
        getADErrorInfo = errorDict['info'].split(", ")

        for item in getADErrorInfo:
            if "data" in item:
                dataCodeList = item.split(" ")
                dataCode = dataCodeList[1]
            if "comment" in item:
                errorMessageList = item.split(":")
                errorMessage = errorMessageList[1]

        if dataCode == "775":
            error = 'your account is locked...\n' + 'visit this site to unlock it.\n' + adSelfServiceSite
        elif dataCode == "52e":
            error = 'username / password mismatch' #+ str(e)
        elif ldapServerDown in str(e):
            error = "AD server: " + ldapServer + " not available"
        elif "In order to perform this operation a successful bind must be completed on the connection" in errorMessage:
            error = "You've lost connectivity to the LDAP server: " + ldapServer  + ". Please log off and on again."
        else:
            error = 'something failed...\n' + str(e)

    except ldap.NO_SUCH_OBJECT as e:
        error = "can't find user: " + uid

    except ldap.SERVER_DOWN:
        error = "AD server: " + ldapServer + " not available"

    except Exception as e:
        capturedError = str(e)

        if uid == "":
            error = "No username entered... Please try again."
        elif "'list' object has no attribute 'items'" in capturedError and uid != "":
            error = "can't find user: " + uid
        else:
            error = 'something failed...\n' + str(e)

    if error is None:
        visibility = "visibility_on"
        searchUser = uid
        displayLockStatus = userLocktatus

    if conn:
        # unbind connection to ldap server
        conn.unbind()

# logout method
def logout():
    user = request.form['username']

    try:
        error = None
        session.pop('sleutel', None)
        session.pop('logged_in', None)
        session.pop('logged_in_user', None)
        session.pop('sessEncPwd', None)
        session.pop('sessIDMEncPwd', None)
        session.pop('already_logged_in', None)
        session.pop('servers_found_in_puppet_list', None)
        session.pop('servers_not_found_in_puppet_list', None)
        session.pop('servers_in_vsphere_list', None)
        session.pop('vcs_vms_in_vspheredb_dict', None)
        session.pop('servers_not_in_vsphere_list', None)
        session.pop('list_of_servers_able_to_ssh', None)
        session.pop('list_of_servers_unable_to_ssh', None)
        session.pop('servers_in_satellite_list', None)
        session.pop('servers_not_in_satellite_list', None)
        session.pop('server_names_list', None)
        session.pop('list_of_VM_info_Lists', None)
        session.pop('cant_find_vms_list', None)
        session.pop('found_vcs_list', None)
        session.pop('found_vms_visibility', None)
        session.pop('cant_find_vms_vc_visibility', None)
        session.pop('display_decomm_heading_value', None)
        session.pop('display_select_results_decomm_db', None)
        session.pop('display_total_records_decomm_db', None)
        session.pop('page_to_go_back_to_decomm_db_querying', None)
        session.clear()

        infoMessage = "user: '{}' logged out.".format(user)
        print(infoMessage)
        logging.info(infoMessage)

    except Exception as e:
        error = 'Exception caught:\n' + str(e)
        print(error)
        logging.info(error)
