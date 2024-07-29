#!/home/johnp/Documents/programming/python/environments/my-py/bin/python3
import ldap, warnings, getpass, sys, io, ast
from contextlib import redirect_stdout
from termcolor import colored, cprint

# variable declaration:
ldapServer = "ldap://<ldap sevrer>"
ldapBase = "<ldap base domain>"
userDomain = "@<domain>"
scriptVers = "2.1.0"
# initialize the con variable (connection to ldap server)
con = ldap.initialize(ldapServer)
user = None
password = None

print("Welcome to the LDAP tool. V:", scriptVers)
print()

# method which prompts the user executing this script to authenticate on AD first.
def authenticate():
    print("You need to authenticate on the " + userDomain + " domain before we proceed...")
    while True:
        try:
            print(colored('please input YOUR username:', 'cyan'))
            user = input()
            print(colored('please input YOUR password:', 'cyan'))
            password = getpass.getpass()

            # set ldap protocol version & options
            con.protocol_version = ldap.VERSION3
            con.set_option(ldap.OPT_REFERRALS, 0)
            # connect / bind to ldap server
            if userDomain in user:
                con.simple_bind_s(user, password)
            elif userDomain not in user:
                con.simple_bind_s((user + userDomain), password)
            #print(con.whoami_s()) # -> test that connection to AD successful.
            break;

        except ldap.LDAPError as e:
            print(colored("failed to connect to ldap server: '{}'".format(ldapServer), 'red'))
            # the below will read the output (stdout) of the exception that was caught
            # from line: print(e)
            # and will store it in a variable
            with io.StringIO() as buf, redirect_stdout(buf):
                print(e)
                errorOutputStr = buf.getvalue()
            # this converts the output (str format) to a dictionary,
            # so that we can find the relevant failure information from key: 'info'
            errorOutputDict = ast.literal_eval(errorOutputStr)
            getADErrorInfo = errorOutputDict['info'].split(", ")
            dataCode = str
            for item in getADErrorInfo:
                if "data" in item:
                    dataCodeList = item.split(" ")
                    dataCode = dataCodeList[1]
            if dataCode == "775":
                print(colored("your account is locked...", 'red'))
                print(colored("visit the below site to unlock it.", 'red'))
                print("https://<reset pwd site>:8443/")
            elif dataCode == "52e":
                print(colored("username / password mismatch...", 'red'))
            con.unbind()
            sys.exit()

        except ldap.INVALID_CREDENTIALS:
            print(colored("your credentials are invalid...", 'red'))
            con.unbind()

        except ldap.NO_SUCH_OBJECT as e:
            print(colored("can't find user: '{}'".format(user), 'red'))
            print(e)
            con.unbind()

        except ldap.SERVER_DOWN:
           print(colored("AD server: '{}' not available".format(ldapServer), 'red'))
           con.unbind()

        except Exception as e:
            print(colored("something failed...", 'red'))
            print(e)
            con.unbind()
            sys.exit()

        except KeyboardInterrupt as ki:
            print()
            print(colored("User initiated a Keyboard Interrupt...", 'grey'))
            print(colored("Quiting LDAP tool", 'grey'))
            # con.unbind()
            sys.exit()

        except EOFError as ee:
            print()
            print(colored("User initiated a Keyboard Interrupt...", 'grey'))
            print(colored("Quiting LDAP tool", 'grey'))
            # con.unbind()
            sys.exit()

# method to allow user to select what they want to do...
def selectMethod():
    while True:
        try:
            print()
            print(colored("Please select an option:", 'magenta'))
            print(colored("1. Get AD INFO for a specific user", 'magenta'))
            print(colored("2. Get list of Groups that a user is in", 'magenta'))
            print(colored("3. Get list of members for a specific Group", 'magenta'))
            print(colored("4. Check if a user is locked out", 'magenta'))
            print(colored("5. exit", 'magenta'))
            print(colored("enter in the no. only of the option:\n", 'magenta'))
            userSelect = int(input())

            if userSelect == 1:
                while True:
                    print()
                    print(colored('please input username to search:', 'yellow'))
                    uid = input()
                    if " " in uid and "," not in uid:
                        print(colored('usage: firstname, lastname', 'red'))
                    elif "," in uid or " " in uid:
                        # set search query based on user input
                        query = '(cn=%s)' % uid
                        ldapSearchUser(user, password, uid, query)
                        break;
                    else:
                        # set search query based on user input
                        wildCardUID = "*" + uid[1:] + "*"
                        # query = '(sAMAccountName=%s)' % uid
                        query = '(sAMAccountName=%s)' % wildCardUID
                        ldapSearchUser(user, password, uid, query)
                        break;

            elif userSelect == 2:
                while True:
                    print()
                    print(colored('please input username to search:', 'yellow'))
                    uid = input()
                    if " " in uid and "," not in uid:
                        print(colored('usage: firstname, lastname', 'red'))
                    elif "," in uid or " " in uid:
                        # set search query based on user input
                        query = '(cn=%s)' % uid
                        ldapSearchGroups(user, password, uid, query)
                        break;
                    else:
                        # set search query based on user input
                        wildCardUID = "*" + uid[1:] + "*"
                        # query = '(sAMAccountName=%s)' % uid
                        query = '(sAMAccountName=%s)' % wildCardUID
                        ldapSearchGroups(user, password, uid, query)
                        break;

            elif userSelect == 3:
                print()
                print(colored('please input group name to search: ', 'yellow'))
                gid = input()
                ldapSearchGroupMembership(user, password, gid)

            elif userSelect == 4:
                while True:
                    print()
                    print(colored('please input username to search:', 'yellow'))
                    uid = input()
                    if " " in uid and "," not in uid:
                        print(colored('usage: firstname, lastname', 'red'))
                    elif "," in uid or " " in uid:
                        query = '(cn=%s)' % uid
                        ldapSearchUserLock(user, password, uid, query)
                        break;
                    else:
                        wildCardUID = "*" + uid[1:] + "*"
                        # query = '(sAMAccountName=%s)' % uid
                        query = '(sAMAccountName=%s)' % wildCardUID
                        ldapSearchUserLock(user, password, uid, query)
                        break;

            elif userSelect == 5:
                print()
                print(colored("thanks for coming...", 'grey'))
                print(colored("goodbye...", 'grey'))
                con.unbind()
                sys.exit()

            else:
                print()
                print(colored("Invalid option, please try again...", 'red'))

        except ValueError as ve:
            print(colored("You did NOT enter in a valid number value...", 'red'))
            print(colored("please try again...", 'red'))

        except KeyboardInterrupt as ki:
            print()
            print(colored("User initiated a Keyboard Interrupt...", 'grey'))
            print(colored("Quiting LDAP tool", 'grey'))
            con.unbind()
            sys.exit()

        except EOFError as ee:
            print()
            print(colored("User initiated a Keyboard Interrupt...", 'grey'))
            print(colored("Quiting LDAP tool", 'grey'))
            con.unbind()
            sys.exit()

# method for searching and returning info for a specified AD user
def ldapSearchUser(user, password, uid, query):
    try:
        # search ldap server
        i = 0
        resultList = con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query)

        for listItem in resultList[:-1]:
            resultTup = resultList[i]
            i = i + 1
            userDetailsDict = resultTup[1]

            # if statements below check if specic fields of the user are defined.
            # if they are not defined, varible set to empty.
            if 'personalTitle' in userDetailsDict.keys():
                userTitle = userDetailsDict["personalTitle"][0].decode()
            else:
                userTitle = ""

            if 'displayName' in userDetailsDict.keys():
                userFullName = userDetailsDict["displayName"][0].decode()
            else:
                userFullName = ""

            # if 'employeeID' in userDetailsDict.keys():
            if 'sAMAccountName' in userDetailsDict.keys():
                # userEmpID = userDetailsDict["employeeID"][0].decode()
                userEmpID = userDetailsDict["sAMAccountName"][0].decode()
            else:
                userEmpID = ""

            if 'title' in userDetailsDict.keys():
                userJobTitle = userDetailsDict["title"][0].decode()
            else:
                userJobTitle = ""

            if 'whenCreated' in userDetailsDict.keys():
                userJoinDateList = userDetailsDict["whenCreated"][0].decode().split(".")
                userJoinDate = userJoinDateList[0]
                userJoinYear = userJoinDate[:4]
                userJoinMonth = userJoinDate[4:6]
                userJoinDay = userJoinDate[6:8]
            else:
                userJoinYear = ""
                userJoinMonth = ""
                userJoinDay = ""

            if 'physicalDeliveryOfficeName' in userDetailsDict.keys():
                userCompCode = userDetailsDict["physicalDeliveryOfficeName"][0].decode()
            else:
                userCompCode = ""

            if 'businessCategory' in userDetailsDict.keys():
                userCostCenter = userDetailsDict["businessCategory"][0].decode()
            else:
                userCostCenter = ""

            if 'manager' in userDetailsDict.keys():
                userManagerList = userDetailsDict["manager"][0].decode().split(",")
                userManager = (userManagerList[0] + userManagerList[1]).replace("CN=","").replace("\\",",")
            else:
                userManager = ""

            if 'mail' in userDetailsDict.keys():
                userEmail = userDetailsDict["mail"][0].decode()
            else:
                userEmail = ""

            if 'telephoneNumber' in userDetailsDict.keys():
                userTelNumber = userDetailsDict["telephoneNumber"][0].decode()
            else:
                userTelNumber = ""

            if 'mobile' in userDetailsDict.keys():
                userMobNumber = userDetailsDict["mobile"][0].decode()
            else:
                userMobNumber = ""

            if 'loginShell' in userDetailsDict.keys():
                userLoginShell = userDetailsDict["loginShell"][0].decode()
            else:
                userLoginShell = ""

            if 'loginShell' in userDetailsDict.keys():
                userHomeDir = userDetailsDict["unixHomeDirectory"][0].decode()
            else:
                userHomeDir = ""

            cprint('See AD info below for user: ' + userEmpID, 'blue', attrs=['bold'])
            print(colored('Title:{0:16} {1}'.format('',userTitle),'blue'))
            print(colored('Full Name:{0:12} {1}'.format('',userFullName),'blue'))
            print(colored('Employee No:{0:10} {1}'.format('',userEmpID),'blue'))
            print(colored('Job Title:{0:12} {1}'.format('',userJobTitle),'blue'))
            print(colored('Join Date:{0:12} {1}/{2}/{3}'.format('',userJoinYear,
            userJoinMonth, userJoinDay),'blue'))
            print(colored('Company Code:{0:9} {1}'.format('',userCompCode),'blue'))
            print(colored('Cost Centre:{0:10} {1}'.format('',userCostCenter),'blue'))
            print(colored('Manager:{0:14} {1}'.format('',userManager),'blue'))
            print(colored('Email Address:{0:8} {1}'.format('',userEmail),'blue'))
            print(colored('Tel Number:{0:11} {1}'.format('',userTelNumber),'blue'))
            print(colored('Cell Number:{0:10} {1}'.format('',userMobNumber),'blue'))
            print(colored('Default Logon Shell:{0:2} {1}'.format('',userLoginShell),'blue'))
            print(colored('Default Home Dir:{0:5} {1}'.format('',userHomeDir),'blue'))

            print()
            print()


    except ldap.LDAPError as e:
        print(colored("failed to connect to ldap server: '{}'".format(ldapServer), 'red'))

    except ldap.NO_SUCH_OBJECT as e:
        print(colored("can't find user: '{}'".format(uid), 'red'))
        print(e)

    except ldap.SERVER_DOWN:
       print(colored("AD server: '{}' not available".format(ldapServer), 'red'))

    except Exception as e:
        print(colored("something failed...", 'red'))
        print(e)

    except KeyboardInterrupt as ki:
        print(colored("User initiated a Keyboard Interrupt...", 'grey'))
        print(colored("Quiting LDAP tool", 'grey'))
        sys.exit()

# method for searching and returning the AD groups a user belongs to
def ldapSearchGroups(user, password, uid, query):
    try:
        # search ldap server
        resultList = con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['memberOf',])
        print(resultList)
        resultTup = resultList[0]
        userDetails = resultTup[0]
        userGroupsDict = resultTup[1]
        groupNameList = []

        for key, value in userGroupsDict.items():
            for item in value:
                decoded_item = item.decode()
                group = decoded_item.split(",")
                # group value: ['CN=xxx', 'OU=xxx', 'DC=xxx', 'DC=xx', 'DC=xx']
                # [0] for first item in the list "group"
                groupName = group[0].split("=")
                # groupName value: ['CN', '<AD group name>']
                # [1] for second item in list "groupName"
                groupNameList.append(groupName[1])

        print()
        if len(groupNameList) > 0:
            cprint('user: ' + uid + ' exists in the below groups:', 'blue', attrs=['bold'])
            for item in groupNameList:
                print(colored(item, 'blue'))
        else:
            print(colored('user: ' + uid + ' does not belong to any groups', 'yellow'))

    except ldap.LDAPError as e:
        print(colored('failed to connect to ldap server: ' + ldapServer, 'red'))

    except ldap.NO_SUCH_OBJECT as e:
        print(colored("can't find user: " + uid, 'red'))
        print(e)

    except ldap.SERVER_DOWN:
       print(colored("AD server: " + ldapServer + " not available", 'red'))

    except Exception as e:
        print(colored("something failed...", 'red'))
        print(e)

    except KeyboardInterrupt as ki:
        print(colored("User initiated a Keyboard Interrupt...", 'grey'))
        print(colored("Quiting LDAP tool", 'grey'))
        sys.exit()

# method for checking whose members of a certain group
def ldapSearchGroupMembership(user, password, gid):
    try:
        # set search query
        query = '(cn=%s)' % gid
        # search ldap server
        resultList = con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['member',])
        print(resultList)
        resultTup = resultList[0]
        resultDict = resultTup[1]
        memberNameList = []

        for key, value in resultDict.items():
            for item in value:
                decoded_item = item.decode()
                member = decoded_item.split(",")
                # member value: ['CN=Paulsen\\', ' John', 'OU=DomainUsers', 'DC=<dc>', 'DC=<dc>', 'DC=<dc>']
                # [0] for last name , [1] for fist name in the list "member"
                fullMemberName = (member[0] + member[1])
                memberName = fullMemberName.split("=")
                # memberName value: ['CN', 'Paulsen\\ John']
                # [1] for second item in list "memberName"
                memberNameList.append(memberName[1])

        print()
        cprint('group: ' + gid + ' contains the below members:', 'blue', attrs=['bold'])
        for item in memberNameList:
            if "OU" in item:
                print(colored(item.replace("OU",""), 'blue'))
            else:
                print(colored(item.replace("\\",","), 'blue'))

    except ldap.LDAPError as e:
        print(colored("failed to connect to ldap server: '{}'".format(ldapServer), 'red'))

    except ldap.NO_SUCH_OBJECT as e:
        print(colored("can't find user: '{}'".format(member), 'red'))
        print(e)

    except ldap.SERVER_DOWN:
       print(colored("AD server not available", 'red'))
    except Exception as e:
        print(colored("something failed...", 'red'))
        print(e)

    except KeyboardInterrupt as ki:
        print(colored("User initiated a Keyboard Interrupt...", 'grey'))
        print(colored("Quiting LDAP tool", 'grey'))
        sys.exit()

# method for checking if a users account is locked out.
def ldapSearchUserLock(user, password, uid, query):
    try:
        # search ldap server
        resultAllList = con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query)
        print(resultAllList)
        resultLockTimeList = con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['lockoutTime',])
        resultLockDurationList = con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['lockoutDuration',])
        # print(resultAllList)
        # print(resultLockTimeList)
        # print(resultLockDurationList)
        resultLockTimeTup = resultLockTimeList[0]
        userLockTimeDetails = resultLockTimeTup[0]
        userLockTimeDict = resultLockTimeTup[1]

        for key, value in userLockTimeDict.items():
            userLockTime = int(value[0].decode())
            if userLockTime == 0:
                # print(uid, "is NOT locked")
                print(colored("'{}' is NOT locked".format(uid), 'green'))
            elif userLockTime != 0:
                # print(uid, "IS LOCKED")
                print(colored("'{}' IS LOCKED".format(uid), 'red'))
            else:
                print(colored("determining lock status of: '{}' failed...".format(uid), 'yellow'))()

    except ldap.LDAPError as e:
        print(colored("failed to connect to ldap server: '{}'".format(ldapServer), 'red'))

    except ldap.NO_SUCH_OBJECT as e:
        print(colored("can't find user: '{}'".format(uid), 'red'))
        print(e)

    except ldap.SERVER_DOWN:
       print(colored("AD server: '{}' not available".format(ldapServer), 'red'))
    except Exception as e:
        print(colored("something failed...", 'red'))
        print(e)

    except KeyboardInterrupt as ki:
        print(colored("User initiated a Keyboard Interrupt...", 'grey'))
        print(colored("Quiting LDAP tool", 'grey'))
        sys.exit()

# calling the method/s
authenticate()
selectMethod()
