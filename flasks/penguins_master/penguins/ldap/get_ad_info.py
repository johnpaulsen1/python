import functools, ldap, io, ast, warnings, sys
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)
from ldap.controls import SimplePagedResultsControl
from cryptography.fernet import Fernet
import ssl
from pubsub import pub
from penguins.other_utils import general
from penguins.auth import (logout, decryptPwd, encryptPwd, domain,
    userDomain, ldapServer, ldapBase, ldapServerDown, adSelfServiceSite
)

def init_ldap_con(con, this_key):
    try:
        error = None
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        con = ldap.initialize(ldapServer)
        user = session.get('logged_in_user')
        encPwd = session.get('sessEncPwd')

        # set ldap protocol version & options for ldaps
        con.set_option(ldap.OPT_REFERRALS, 0)
        con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        con.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
        con.set_option(ldap.OPT_X_TLS_DEMAND, True)
        con.set_option(ldap.OPT_DEBUG_LEVEL, 255)

        if userDomain not in user:
            user = user + userDomain

        # connect / bind to ldap server
        con.simple_bind_s(user, decryptPwd(encPwd, this_key))

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
            error = "AD server: " + ldapServer + " not available"
        elif "In order to perform this operation a successful bind must be completed on the connection" in errorMessage:
            error = "You've lost connectivity to the LDAP server: " + ldapServer  + ". Please log off and on again."
        else:
            error = 'something failed...\n' + str(e)

    except ldap.INVALID_CREDENTIALS:
        error = 'your credentials are invalid...'

    except ldap.NO_SUCH_OBJECT as e:
        error = "can't find user: " + user

    except ldap.SERVER_DOWN:
        error = "AD server: " + ldapServer + " not available"

    except Exception as e:
        error = 'something failed...\n' + str(e)

    return con

def getUserName(user):
    userFullName = ""
    con = ldap.initialize(ldapServer)
    _key = session.get('sleutel')
    established_ldap_con = init_ldap_con(con, _key)
    query = '(sAMAccountName={})'.format(user)

    try:
        # search ldap server
        resultList = established_ldap_con.search_s(ldapBase, ldap.SCOPE_SUBTREE, query)
        i = 0
        for listItem in resultList[:-1]:
            resultTup = resultList[i]
            i = i + 1
            userDetailsDict = resultTup[1]

            if 'displayName' in userDetailsDict.keys():
                userFullName = userDetailsDict["displayName"][0].decode()
            else:
                userFullName = "N/A"

    except Exception as e:
        error = 'something failed...\n' + str(e)

    return userFullName
