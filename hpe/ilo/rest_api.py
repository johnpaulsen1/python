#!/usr/bin/env python

import argparse
import redfish
import json
from getpass import getpass

parser = argparse.ArgumentParser(description="Python script that interacts with the redfish api via http requests, this is still WIP...")

parser.add_argument('--ilo-uri', '-iu', type=str,
                    help='Specify the ilo URI that redfish will use to interact with.\n'+
                    "EXAMPLE: '/redfish/v1/systems/1'\n"+
                    "Refer to the redfish api documentation for more information.\n"+
                    "See URL: https://servermanagementportal.ext.hpe.com/docs/redfishservices/ilos/ilo5/ilo5_296/ilo5_resmap296/",
                    dest='ilo_uri', required=True)
parser.add_argument('--http-request', '-r', type=str,
                    help='Specify what type of http request to perform',
                    choices=['GET', 'POST', 'PATCH', 'DELETE'],
                    dest='http_request', required=True)
parser.add_argument('--http-body', '-b', type=str,
                    help='Specify the http request body to send with the http request, it must be a valid json string. (OPTIONAL).\n'+
                    "EXAMPLE: '{\"key\": \"value\"}'",
                    dest='http_body', required=False)
parser.add_argument('--search-attrib', '-sa', type=str,
                    help="Specify a search attribute to use when using the 'GET' http-request (OPTIONAL).\n"+
                    "If not specified, the script will print the entire response body.",
                    dest='search_attrib', required=False)
parser.add_argument('--ilo-ip', '-i', type=str,
                    help='Specify the ilo ip address',
                    dest='ilo_ip', required=True)
parser.add_argument('--ilo-user', '-u', type=str,
                    help='Specify the ilo username',
                    dest='ilo_user', required=False)
parser.add_argument('--ilo-password', '-p', type=str,
                    help='Specify the ilo password',
                    dest='ilo_password', required=False)
parser.add_argument('--ansible', '-a', type=bool,
                    help='Using this switch LIMITS output needed specifically for Anisble Playbooks ONLY.',
                    choices=[True, False],
                    default=False,
                    dest='ansible', required=False)

args = parser.parse_args()

ansible = args.ansible
http_request = args.http_request
http_body = str(args.http_body) if args.http_body != None else None
try:
    http_body_dict = json.loads(http_body) if http_body != None else None
except Exception as e:
    if not ansible:
        print("Failed to convert http body: '{}' to a valid json string...".format(http_body))
        print("Please ensure that the http body follows format: '{\"key\": \"value\"}'")
        print("Error:")
        print(str(e))
    exit(1)
search_attrib = args.search_attrib
ilo_ip = args.ilo_ip
# ilo_user = args.ilo_user
# ilo_password = args.ilo_password
# ilo_uri = "/redfish/v1/systems/1"
# ilo_uri = "/redfish/v1/managers/1/NetworkProtocol/"
ilo_uri = args.ilo_uri
dash_line = '-' * 80
star_line = '*' * 80
hash_line = '#' * 65

def ansible_switch_test():
    fail_script = False
    ilo_user = args.ilo_user
    ilo_password = args.ilo_password
    if not ansible:
        if ilo_user != None:
            fail_script = True
            print("You should NOT specify the ilo username, the script will prompt you for this information...")
            print("This functinality is reserved only for use with Ansible Playbooks...")
            print()
        if ilo_password != None:
            fail_script = True
            print("You should NOT specify the ilo password, the script will prompt you for this information...")
            print("This functinality is reserved only for use with Ansible Playbooks...")
            print()
    if fail_script:
        exit(1)

def get_ilo_credentials():
    ilo_credentials = list()
    print(hash_line)
    print('get_ilo_credentials()')
    print("Please enter the ilo username and password...")

    ilo_user = input("ilo username:\n")
    ilo_credentials.append(ilo_user)
    
    ilo_password = getpass("ilo password:\n")
    ilo_credentials.append(ilo_password)
    
    print(hash_line)
    return ilo_credentials

def ilo_login(ilo_ip):
    # test how the script is being run.
    ansible_switch_test()
    ilo_url = "https://" + ilo_ip + "/"
    if not ansible:
        print(hash_line)
        print('ilo_login()')
        # if ilo_user and ilo_password are not specified, prompt the user for the ilo credentials.
        ilo_credentials_list = get_ilo_credentials()
        ilo_user = ilo_credentials_list[0]
        ilo_password = ilo_credentials_list[1]
        print("attempting to login to ilo: '{}'".format(ilo_url))
    if ansible:
        ilo_user = args.ilo_user
        ilo_password = args.ilo_password

    try:
        redfish_obj = redfish.redfish_client(base_url=ilo_url, username=ilo_user, password=ilo_password)
    except Exception as e:
        if not ansible:
            print("Error:")
            print(str(e))
        exit(1)
    
    try:
        redfish_obj.login(auth="session")
    except Exception as e:
        if not ansible:
            print("Error:")
            print(str(e))
        exit(1)
    
    if not ansible:
        print("successfully logged in to ilo: '{}'".format(ilo_url))
        print(hash_line)
    
    return redfish_obj

def ilo_logout(redfish_obj):
    if not ansible:
        print(hash_line)
        print('ilo_logout()')
        print("attempting to logout from ilo: '{}'".format(ilo_ip))
    try:
        redfish_obj.logout()
    except Exception as e:
        if not ansible:
            print("Error:")
            print(str(e))
        exit(1)
    if not ansible:
        print("successfully logged out from ilo: '{}'".format(ilo_ip))
        print(hash_line)

def get_http_request():
    if not ansible:
        print('get_http_request()')
    try:
        redfish_obj = ilo_login(ilo_ip)
    except Exception as e:
        if not ansible:
            print("Error:")
            print(str(e))
        exit(1)
    
    try:
        response = redfish_obj.get(ilo_uri)
    except Exception as e:
        if not ansible:
            print("Error:")
            print(str(e))
        exit(1)
    if not ansible:
        print()
        print(dash_line)
        print("http '{}' request response status:".format(http_request))
        print(response.status)
        print(dash_line)

    if response.status == 200:
        if search_attrib == None:
            if not ansible:
                print("no search attribute specified, showing you the entire response body, in the format of:\n"+
                    "key: '<key>' => value: '<value>'")
                print("http '{}' request response body:".format(http_request))
                print()
                for key, value in response.dict.items():
                        print("key: '{}' => value: '{}'".format(key, value))
        else:
            attrib_found = False
            if not ansible:
                print("searching for attribute: '{}'".format(search_attrib))
            for key, value in response.dict.items():
                if key == search_attrib:
                    attrib_found = True
                    # this print statement will be used by Ansible.
                    # that is why there's no "if not ansible:" statement for this print.
                    print("key: '{}' => value: '{}'".format(key, value))
                    break
            if not attrib_found:
                # this print statement will be used by Ansible.
                # that is why there's no "if not ansible:" statement for this print.
                print("attribute '{}' not found in response body...".format(search_attrib))
                if not ansible:
                    print("showing you the response body instead, in the format of:\n"+
                    "key: '<key>' => value: '<value>'")
                    for key, value in response.dict.items():
                        print("key: '{}' => value: '{}'".format(key, value))
        if not ansible:
            print(dash_line)
            print()
    else:
        if not ansible:
            print("http '{}' request did not return the expected result...".format(http_request))
            print('response status: {}'.format(response.status))
            print()
            for key, value in response.dict.items():
                print("key: '{}' => value: '{}'".format(key, value))
            print()
            print(dash_line)
    
    try:
        ilo_logout(redfish_obj)
    except Exception as e:
        if not ansible:
            print("Error:")
            print(str(e))
        exit(1)
    
def post_http_request():
    if not ansible:
        print('post_http_request()')
    
    if http_body == None or http_body == '':
        if not ansible:
            print('http_body is empty.')
            print("For this type of http request:'{}', you must specify a valid http body.".format(http_request))
            print('Please specify a valid http body.')
            print("Using the switch '--http-body' or '-b'")
        exit(1)
    
    try:
        redfish_obj = ilo_login(ilo_ip)
    except Exception as e:
        if not ansible:
            print("Error:")
            print(str(e))
        exit(1)
    
    try:
        response = redfish_obj.post(ilo_uri, body=http_body_dict)
    except Exception as e:
        if not ansible:
            print("Error:")
            print(str(e))
        exit(1)
    if not ansible:
        print()
        print(dash_line)
        print("http '{}' request response status:".format(http_request))
        print(response.status)
        print(dash_line)

    # these print statements will be used by Ansible.
    # that is why there's no "if not ansible:" statement for these.
    if response.status == 200:
        print("successful '{}' request to ilo uri: '{}' using data key: '{}' and value: '{}'".format(http_request, ilo_uri, list(http_body_dict.keys())[0], list(http_body_dict.values())[0]))
        print('see response body for more information...')
        print("response body:")
        print(str(response.dict))
    else:
        print("http '{}' request did not return the expected result...".format(http_request))
        print('response status: {}'.format(response.status))
        print()
        print("please review the response body for more information...")
        print("response body:")
        print(str(response.dict))
    
    if not ansible:
        print(dash_line)
        print()

def patch_http_request():
    if not ansible:
        print('patch_http_request()')
    
    if http_body == None or http_body == '':
        if not ansible:
            print('http_body is empty.')
            print("For this type of http request: '{}', you must specify a valid http body.".format(http_request))
            print('Please specify a valid http body.')
            print("Using the switch '--http-body' or '-b'")
        exit(1)
    
    try:
        redfish_obj = ilo_login(ilo_ip)
    except Exception as e:
        if not ansible:
            print("Error:")
            print(str(e))
        exit(1)
    
    try:
        response = redfish_obj.patch(ilo_uri, body=http_body_dict)
    except Exception as e:
        if not ansible:
            print("Error:")
            print(str(e))
        exit(1)
    if not ansible:
        print()
        print(dash_line)
        print("http '{}' request response status:".format(http_request))
        print(response.status)
        print(dash_line)

    # these print statements will be used by Ansible.
    # that is why there's no "if not ansible:" statement for these.
    if response.status == 200:
        print("successful '{}' request to ilo uri: '{}' using data key: '{}' and value: '{}'".format(http_request, ilo_uri, list(http_body_dict.keys())[0], list(http_body_dict.values())[0]))
        print('see response body for more information...')
        print("response body:")
        print(str(response.dict))
    else:
        print("http '{}' request did not return the expected result...".format(http_request))
        print('response status: {}'.format(response.status))
        print()
        print("please review the response body for more information...")
        print("response body:")
        print(str(response.dict))
    
    if not ansible:
        print(dash_line)
        print()

def delete_http_request():
    if not ansible:
        print('delete_http_request()')

    if http_body == None or http_body == '':
        if not ansible:
            print('http_body is empty.')
            print("For this type of http request: '{}', you must specify a valid http body.".format(http_request))
            print('Please specify a valid http body.')
            print("Using the switch '--http-body' or '-b'")
        exit(1)

def main():
    match http_request:
        case 'GET':
            if not ansible:
                print(star_line)
            get_http_request()
            if not ansible:
                print(star_line)
        case 'POST':
            if not ansible:
                print(star_line)
            post_http_request()
            if not ansible:
                print(star_line)
        case 'PATCH':
            if not ansible:
                print(star_line)
            patch_http_request()
            if not ansible:
                print(star_line)
        case 'DELETE':
            if not ansible:
                print(star_line)
            delete_http_request()
            if not ansible:
                print(star_line)
        case _:
            print('Invalid http request, please specify a valid http request...')
            exit(1)

if __name__ == '__main__':
    main()
