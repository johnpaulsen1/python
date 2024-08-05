#!/usr/bin/python3
from cryptography.fernet import Fernet
import getpass

da_oukie_filename = "not_today.txt"
da_sleutel_filename = "not_yesterday.txt"
passy_filename = "not_ever.txt"

def check_da_dip():
    da_oukie_is_there = False
    da_oukie = None

    da_sleutel_is_there = False
    da_sleutel = None

    passy_is_there = False
    passy = None

    # open above files
    try:
        da_oukie_file = open(da_oukie_filename)
    except IOError:
        print("File: '{}' not accessible".format(da_oukie_filename))

    try:
        da_sleutel_file = open(da_sleutel_filename)
    except IOError:
        print("File: '{}' not accessible".format(da_sleutel_filename))

    try:
        passy_file = open(passy_filename)
    except IOError:
        print("File: '{}' not accessible".format(passy_filename))


    # check that the files are not empty
    for line in da_oukie_file.readlines():
        if line != None or line != "":
            da_oukie_is_there = True
            da_oukie = line
            da_oukie_file.close()
            break;

    for line in da_sleutel_file.readlines():
        if line != None or line != "":
            da_sleutel_is_there = True
            da_sleutel = line
            da_sleutel_file.close()
            break;

    for line in passy_file.readlines():
        if line != None or line != "":
            passy_is_there = True
            passy = line
            passy_file.close()
            break;

    if da_oukie_is_there and passy_is_there and da_sleutel_is_there:
        print("we have all the ingredients...")
        print()
        da_secret_sauce_list = getTheSecretSauce()
        return da_secret_sauce_list


    if da_oukie_is_there == False or passy_is_there == False or da_sleutel_is_there == False:
        print("we're missing some ingredients...")
        print("let's go to the supermarket to get em...")
        print()

        user = input("input username to encrypt: ")
        pwd = getpass.getpass("input password to encrypt: ")
        encrypty_da_passy(user, pwd)
        print("we should have all the ingredients now... :-)")
        da_secret_sauce_list = getTheSecretSauce()
        return da_secret_sauce_list


def encrypty_da_passy(username, password):
    try:
        key = Fernet.generate_key()
    except Exception as e:
        print("unable to generate key.")
        print("error:")
        print(e)

    try:
        da_sleutel_file = open(da_sleutel_filename, "w")
        da_sleutel_file.write(str(key.decode()))
    except IOError:
        print("File: '{}' not accessible".format(da_sleutel_filename))

    encoded_username = username.encode()
    encoded_password = password.encode()
    cipher_suite = Fernet(key)
    encrypted_username = cipher_suite.encrypt(encoded_username)
    encrypted_password = cipher_suite.encrypt(encoded_password)

    try:
        da_oukie_file = open(da_oukie_filename, "w")
        da_oukie_file.write(str(encrypted_username.decode()))
    except IOError:
        print("File: '{}' not accessible".format(da_oukie_filename))

    try:
        passy_file = open(passy_filename, "w")
        passy_file.write(str(encrypted_password.decode()))
    except IOError:
        print("File: '{}' not accessible".format(passy_filename))


def getTheSecretSauce():
    da_secret_sauce_list = list()
    da_oukie_is_there = False
    da_oukie = None

    da_sleutel_is_there = False
    da_sleutel = None

    passy_is_there = False
    passy = None

    try:
        da_oukie_file = open(da_oukie_filename)
    except IOError:
        print("File: '{}' not accessible".format(da_oukie_filename))

    try:
        da_sleutel_file = open(da_sleutel_filename)
    except IOError:
        print("File: '{}' not accessible".format(da_sleutel_filename))

    try:
        passy_file = open(passy_filename)
    except IOError:
        print("File: '{}' not accessible".format(passy_filename))

    # get da ingredients
    for line in da_oukie_file.readlines():
        da_oukie_encrypted = line.encode()
        da_oukie_is_there = True
        break;

    for line in da_sleutel_file.readlines():
        da_sleutel = line.encode()
        da_sleutel_is_there = True
        break;

    for line in passy_file.readlines():
        passy_encrypted = line.encode()
        passy_is_there = True
        break;

    if da_oukie_is_there:
        da_secret_sauce_list.append(da_oukie_encrypted)

    if da_sleutel_is_there:
        da_secret_sauce_list.append(da_sleutel)

    if passy_is_there:
        da_secret_sauce_list.append(passy_encrypted)

    return da_secret_sauce_list
