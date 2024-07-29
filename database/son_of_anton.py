#!/usr/bin/env python3
from cryptography.fernet import Fernet
import json

def getTheIngredients(receipe):

    cipher_suite = Fernet(receipe['lock_smith'].encode())
    og_kush = cipher_suite.decrypt(receipe['og_kush_repro'].encode())
    raw_bacon = receipe['bacon'].encode()
    the_son_of_anton = Fernet(og_kush)
    bacon = the_son_of_anton.decrypt(raw_bacon)

    return bacon
