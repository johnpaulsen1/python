#!/usr/bin/python3

import os

cwd = os.getcwd()
source_files_directory = cwd + '/txt_files'


def testdir():
    pass

def createMDfile(mdfile,role,change_number):
    npstatement="""
<b>== GENERAL ==</b><br>
<b> General changes that will need to be actioned during the slot. </b><br>

<b>== TSD LINUX ==</b><br>
<b> TSD Linux specific changes during the slot. </b><br>

<b>=== {} ===</b><br>
<b>NON-PRODUCTION PATCHING  </b><br>

 <b>Tasks to complete before patching:  </b>
* Go through your whole list of servers during the week and ensure that you can log into all the hosts, note the ones you cannot log into - check with a team member if you cannot log in. Otherwise it needs to be fixed on the patching night.<br>
* Get in touch with all your business units by Friday afternoon (before patching) once the server lists are allocated, get a contact person to speak to before and after patching<br>
* NB: Place your hosts into down time on Olympic - [[http://olympic]] - before starting with patching<br>
* See Software updates page - [[Apply_software_updates]]<br>

 <b>Tasks to complete after patching:  </b><br>
* Check the uptime on all your hosts <br>
** Can be done numerous ways. puppet db example:
```
  puppet query facts --facts lsbdistrelease,lsbmajdistrelease,uptime,operatingsystem,fnb_server_role '(uptime_days > 1)' --render-as console
  puppet query facts --facts lsbdistrelease,lsbmajdistrelease,uptime,operatingsystem,fnb_server_role '(uptime_days > 1 and lsbmajdistrelease != 5)' --render-as console
```
or only prod and dr
```
  puppet query facts --facts lsbdistrelease,lsbmajdistrelease,uptime,operatingsystem,fnb_server_role '(uptime_days > 1 and (fnb_server_role=prod or fnb_server_role=dr))' --render-as console
```
* Go to Satellite [[https://<satellite>/]] and ensure that all your hosts are fully updated
* Go to Olympic and ensure that all the services are green - check mount points,services etc.
* Notify all your business units via mail and call them to ensure that they are aware that all their hosts have been patched

""".format(change_number)
    pstatement="""
<b>== GENERAL ==</b><br>
<b> General changes that will need to be actioned during the slot. </b><br>

<b>== TSD LINUX ==</b><br>
<b> TSD Linux specific changes during the slot. </b><br>

<b>=== {} ===</b><br>
<b>PRODUCTION PATCHING</b><br>

 <b>Tasks to complete before patching:</b><br>
* Go through your whole list of servers during the week and ensure that you can log into all the hosts, note the ones you cannot log into - check with a team member if you cannot log in. Otherwise it needs to be fixed on the patching night.
* Get in touch with all your business units by Friday afternoon (before patching) once the server lists are allocated, get a contact person to speak to before and after patching
* NB: Place your hosts into down time on Olympic - [[http://olympic]] - before starting with patching
* See Software updates page - [[Apply_software_updates]]

 <b>Tasks to complete after patching:</b><br>
* Check the uptime on all your hosts
** Can be done numerous ways. puppet db example:<br>
```
  puppet query facts --facts lsbdistrelease,lsbmajdistrelease,uptime,operatingsystem,fnb_server_role '(uptime_days > 1)' --render-as console
  puppet query facts --facts lsbdistrelease,lsbmajdistrelease,uptime,operatingsystem,fnb_server_role '(uptime_days > 1 and lsbmajdistrelease != 5)' --render-as console
```
or only prod and dr<br>
```
  puppet query facts --facts lsbdistrelease,lsbmajdistrelease,uptime,operatingsystem,fnb_server_role '(uptime_days > 1 and (fnb_server_role=prod or fnb_server_role=dr))' --render-as console
* Go to Satellite [[https://<satellite>/]] and ensure that all your hosts are fully updated
* Go to Olympic and ensure that all the services are green - check mount points,services etc.
* Notify all your business units via mail and call them to ensure that they are aware that all their hosts have been patched
```

""".format(change_number)

    with open(mdfile, 'a+') as f:
        if role == 'prod':
            f.write(pstatement)
            print("prod patch page skeleton created.")
        elif role == 'nonprod':
            f.write(npstatement)
            print("nonprod patch page skeleton created")


def testMDfile(mdfile,role,change_number):
    if os.path.exists(mdfile):
        os.remove(mdfile)
        print("old page found and removed...creating new...")
        createMDfile(mdfile,role,change_number)
    else:
        print("markdown file not present...continuing.")
        createMDfile(mdfile,role,change_number)


def addExceptions(mdfile):
    exception_message = '''
<b>==== EXCLUSIONS ====</b><br>
<b> NB: Please mail `change management team` for any BU's that are not patching. </b><br>
'''
    with open(mdfile, 'a+') as f:
        f.write(exception_message)
