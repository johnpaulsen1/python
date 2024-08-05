#!/usr/bin/env python3
import ldap, getpass, sys, io, ast
from contextlib import redirect_stdout
from termcolor import cprint

# variable declaration:
ldapServer = "ldap://<ldap server>/"
ldapBase = "OU=xxx,DC=yyy,DC=zzz,DC=aaa,DC=bbb,DC=ccc"
userDomain = "XYZ"
scriptVers = "0.1.0"
sailPointSite = "https://not-today.com"

# initialize the con variable (connection to ldap server)
con = ldap.initialize(ldapServer)
user = None
password = None

print("Welcome to the LDAP tool. V:", scriptVers)
print()

# method which prompts the user executing this script to authenticate on AD first.
def authenticate():
	print(f"You need to authenticate on the {userDomain} domain before we proceed...")
	while True:
		try:
			cprint('Please input AD username:', 'cyan')
			user = input()
			cprint(f"Please input password for AD user: '{user}':", 'cyan')
			password = getpass.getpass()

			# set ldap protocol version & options
			con.protocol_version = ldap.VERSION3
			con.set_option(ldap.OPT_REFERRALS, 0)
			# connect / bind to ldap server
			con.simple_bind_s(user, password)
			# print(con.whoami_s()) # -> test that connection to AD successful.
			break;

		except ldap.LDAPError as e:
			cprint(f"failed to connect to ldap server: '{ldapServer}'", 'red')
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
				cprint(f"user: '{user}' ldap account is locked...", 'red')
				cprint("visit the below site to unlock it.", 'red')
				print(f"https://{sailPointSite}")
			elif dataCode == "52e":
				cprint("username / password mismatch...", 'red')
			con.unbind()
			sys.exit()

		except ldap.INVALID_CREDENTIALS:
			cprint(f"User: '{user}' credentials are invalid...", 'red')
			con.unbind()

		except ldap.NO_SUCH_OBJECT as e:
			cprint(f"Can't find user: '{user}'", 'red')
			print(e)
			con.unbind()

		except ldap.SERVER_DOWN:
			cprint(f"AD server: '{ldapServer}' not available.", 'red')
			con.unbind()

		except Exception as e:
			cprint("Exception caught:", 'red')
			cprint(e, 'red')
			con.unbind()
			sys.exit()

		except KeyboardInterrupt as ki:
			print()
			cprint("User initiated a Keyboard Interrupt...", 'grey')
			cprint("Quiting LDAP tool", 'grey')
			# con.unbind()
			sys.exit()

		except EOFError as ee:
			print()
			cprint("User initiated a Keyboard Interrupt...", 'grey')
			cprint("Quiting LDAP tool", 'grey')
			# con.unbind()
			sys.exit()

# method to allow user to select what they want to do...
def selectMethod():
	while True:
		try:
			print()
			cprint("Please select an option:", 'magenta')
			cprint("1. Get AD INFO for a specific user", 'magenta')
			cprint("2. Get list of Groups that a user is in", 'magenta')
			cprint("3. Get list of members for a specific Group", 'magenta')
			cprint("4. exit", 'magenta')
			cprint("enter in the no. only of the option:\n", 'magenta')
			userSelect = int(input())

			if userSelect == 1:
				while True:
					print()
					cprint('please input username to search:', 'yellow')
					uid = input()
					if " " in uid and "," not in uid:
						cprint('usage: lastname, firstname', 'red')
					elif " " in uid and "," in uid:
						# set search query based on user input
						query = f"(cn={uid})"
						ldapSearchUser(uid, query)
						break;
					else:
						# # set search query based on user input
						# wildCardUID = f"*{uid[1:]}*"
						# query = f'(sAMAccountName={uid})'
						query = f'(sAMAccountName={uid})'
						ldapSearchUser(uid, query)
						break;

			elif userSelect == 2:
				while True:
					print()
					cprint('please input username to search:', 'yellow')
					uid = input()
					if " " in uid and "," not in uid:
						cprint('usage: lastname, firstname', 'red')
					elif "," in uid or " " in uid:
						# set search query based on user input
						query = f'(cn={uid})'
						ldapSearchGroups(uid, query)
						break;
					else:
						# set search query based on user input
						# wildCardUID = f"*{uid[1:]}*"
						# query = f'(sAMAccountName={uid})'
						query = f'(sAMAccountName={uid})'
						ldapSearchGroups(uid, query)
						break;

			elif userSelect == 3:
				print()
				cprint('please input group name to search: ', 'yellow')
				gid = input()
				ldapSearchGroupMembership(user, gid)

			elif userSelect == 4:
				print()
				cprint("thanks for coming...", 'grey')
				cprint("goodbye...", 'grey')
				con.unbind()
				sys.exit()

			else:
				print()
				cprint("Invalid option, please try again...", 'red')

		except ValueError as ve:
			cprint("You did NOT enter in a valid number value...", 'red')
			cprint("please try again...", 'red')

		except KeyboardInterrupt as ki:
			print()
			cprint("User initiated a Keyboard Interrupt...", 'grey')
			cprint("Quiting LDAP tool", 'grey')
			con.unbind()
			sys.exit()

		except EOFError as ee:
			print()
			cprint("User initiated a Keyboard Interrupt...", 'grey')
			cprint("Quiting LDAP tool", 'grey')
			con.unbind()
			sys.exit()

# method for searching and returning info for a specified AD user
def ldapSearchUser(uid, query):
	cprint(f"Running LDAP Search for user: '{uid}', using query: '{query}'", 'grey', attrs=['bold'])
	try:
		# search ldap server
		i = 0
		resultList = con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query)

		for listItem in resultList:
			resultTup = resultList[i]
			i = i + 1
			userDetailsDict = resultTup[1]

			# if statements below check if specic fields of the user are defined.
			# if they are not defined, varible set to empty.
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

			cprint('See AD info below for user: ' + userEmpID, 'blue', attrs=['bold'])
			cprint('Full Name:{0:12} {1}'.format('',userFullName),'blue')
			cprint('Employee No:{0:10} {1}'.format('',userEmpID),'blue')
			cprint('Job Title:{0:12} {1}'.format('',userJobTitle),'blue')
			cprint('Join Date:{0:12} {1}/{2}/{3}'.format('',userJoinYear,
				userJoinMonth, userJoinDay),'blue')
			cprint('Business Unit:{0:8} {1}'.format('',userCompCode),'blue')
			cprint('Manager:{0:14} {1}'.format('',userManager),'blue')
			cprint('Email Address:{0:8} {1}'.format('',userEmail),'blue')
			cprint('Contact Number:{0:7} {1}'.format('',userTelNumber),'blue')
			print()
			print()

	except ldap.LDAPError as e:
		cprint(f"failed to connect to ldap server: '{ldapServer}'", 'red')

	except ldap.NO_SUCH_OBJECT as e:
		cprint(f"can't find user: '{uid}'", 'red')
		print(e)

	except ldap.SERVER_DOWN:
		cprint(f"AD server: '{ldapServer}' not available", 'red')

	except Exception as e:
		cprint("Exception caught:", 'red')
		cprint(e, 'red')
		sys.exit()

	except KeyboardInterrupt as ki:
		cprint("User initiated a Keyboard Interrupt...", 'grey')
		cprint("Quiting LDAP tool", 'grey')
		sys.exit()

# method for searching and returning the AD groups a user belongs to
def ldapSearchGroups(uid, query):
	cprint(f"Running LDAP Search for Group Membership for user: '{uid}', using query: '{query}'", 'grey', attrs=['bold'])
	try:
		# search ldap server
		resultList = con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['memberOf',])
		resultTup = resultList[0]
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
			cprint(f"user: '{uid}' exists in the below groups:", 'blue', attrs=['bold'])
			for item in groupNameList:
				cprint(item, 'blue')
		else:
			cprint(f"user: '{uid}' does not belong to any groups", 'yellow')

	except ldap.LDAPError as e:
		cprint(f"failed to connect to ldap server: '{ldapServer}'", 'red')

	except ldap.NO_SUCH_OBJECT as e:
		cprint(f"can't find user: '{uid}'", 'red')
		print(e)

	except ldap.SERVER_DOWN:
		cprint(f"AD server: '{ldapServer}' not available", 'red')

	except Exception as e:
		cprint("Exception caught:", 'red')
		cprint(e, 'red')
		sys.exit()

	except KeyboardInterrupt as ki:
		cprint("User initiated a Keyboard Interrupt...", 'grey')
		cprint("Quiting LDAP tool", 'grey')
		sys.exit()

# method for checking whose members of a certain group
def ldapSearchGroupMembership(user, gid):
	# set search query
	query = f'(cn={gid})'
	cprint(f"Running LDAP Search for Members of Group: '{gid}', using query: '{query}'", 'grey', attrs=['bold'])
	membersHash = {}
	try:
		# search ldap server
		resultList = con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['member',])
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
		cprint(f"group: '{gid}' contains the below members:", 'blue', attrs=['bold'])
		for item in memberNameList:
			if "OU" in item:
				user = item.replace("OU","")
			else:
				user = item.replace("\\",",")

			# get the sAMAccountName AD attribute using cn query:
			query = f"(cn={user})"

			resultList = con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query, ['sAMAccountName',])
			resultTup = resultList[0]
			userSamAccDict = resultTup[1]
			userSameAccList = userSamAccDict['sAMAccountName']
			userSameAcc = userSameAccList[0].decode()

			membersHash[user]=userSameAcc

		for key, value in membersHash.items():
			cprint(f'{key} -> {value}','blue')


	except ldap.LDAPError as e:
		cprint(f"failed to connect to ldap server: '{ldapServer}'", 'red')

	except ldap.NO_SUCH_OBJECT as e:
		cprint(f"can't find user: '{member}'", 'red')
		print(e)

	except ldap.SERVER_DOWN:
		cprint(f"AD server: '{ldapServer}' not available", 'red')

	except Exception as e:
		cprint("Exception caught:", 'red')
		cprint(e, 'red')
		sys.exit()

	except KeyboardInterrupt as ki:
		cprint("User initiated a Keyboard Interrupt...", 'grey')
		cprint("Quiting LDAP tool", 'grey')
		sys.exit()

# calling required methods
authenticate()
selectMethod()
