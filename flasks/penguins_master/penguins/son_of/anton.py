#!/usr/bin/env python3
from cryptography.fernet import Fernet
import json

# initialize variables
da_oukie_filename = "not_today.txt"
da_sleutel_filename = "not_tomorrow.txt"
passy_filename = "not_ever.txt"

def getTheIngredients(receipe):

    cipher_suite = Fernet(receipe['lock_smith'].encode())
    og_kush = cipher_suite.decrypt(receipe['og_kush_repro'].encode())
    raw_bacon = receipe['bacon'].encode()
    the_son_of_anton = Fernet(og_kush)
    bacon = the_son_of_anton.decrypt(raw_bacon)

    return bacon

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
