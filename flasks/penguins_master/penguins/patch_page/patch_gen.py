#!/usr/bin/python3

import os
import sys
from . import dbconnect,file_creations,contact,os_commands,git

db = 'linux_cmdb'
table = 'cmdb'

def createLists(dbcon,query,mdfile):
	count = 0
	bu_list = list()
	platform_list = list()
	host_tuple = dbcon.fetchCurrentCMDB(table,db,query)
	for h in host_tuple:
		count += 1
	#	hostname = h[0]
		bu = h[1]
		platform = h[5]
		bu_list.append(bu)
		platform_list.append(platform)
		bu_final = set(bu_list)

	with open(mdfile,'a') as f:
		print(f"==== LINUX PHYSICAL HOST LIST ====")
		f.write(f"<b>==== LINUX PHYSICAL HOST LIST ====</b><br>")
		print(f"Please liaise with the person patching this BU before starting.")
		f.write(f"Please liaise with the person patching this BU before starting.<br>")
		print("<span style=\"color:green\"><b> TEAMMEMBER </b>" )
		f.write("<span style=\"color:green\">Person patching: <b> TEAMMEMBER </b><br>  " )
		pcount = 0
		for bu in sorted(bu_final):
			for h in host_tuple:
				if 'physical' in h:
					if bu in h:
						pcount += 1
						print(f"{pcount}: {h[0]}")
						f.write(f"{pcount}: {h[0]}<br>")
		print()
		f.write('<br>')
	f.close()
	with open(mdfile,'a') as f:
		print(f"==== ZLINUX HOST LIST ====")
		print(f"Please liaise with the person patching this BU before starting.")
		print("<span style=\"color:green\"><b> TEAMMEMBER </b>" )

		f.write(f"<b>==== ZLINUX HOST LIST ====</b><br>")
		f.write(f"Please liaise with the person patching this BU before starting.<br>")
		f.write("<span style=\"color:green\"><b> TEAMMEMBER </b><br>" )
		zcount = 0
		for bu in sorted(bu_final):
			for h in host_tuple:
				if 'zlinux' in h:
					if bu in h:
						zcount += 1
						print(f"{zcount}: {h[0]}")
						f.write(f"{zcount}: {h[0]}<br>")
		print()
		f.write('<br>')
	f.close()

	with open(mdfile,'a') as f:
		print(f"==== LINUX VIRTUAL HOST LIST ====")
		f.write(f"<b>==== LINUX VIRTUAL HOST LIST ====</b><br>")
		f.close()
		for bu in sorted(bu_final):
			vcount = 0
			contact.dl_contacts(bu,mdfile)
			with open(mdfile,'a') as f:
				for h in host_tuple:
					if 'vmware' in h:
						if bu in h:
							vcount += 1
							print(f"{vcount}: {h[0]}")
							f.write(f"{vcount}: {h[0]}<br>")
				f.write('<br>')
				print()

	with open(mdfile,'a') as f:
		print(f"==== LINUX KVM HOST LIST ====")
		print("<span style=\"color:green\"><b> TEAMMEMBER </b>" )
		f.write(f"<b>==== LINUX KVM HOST LIST ====</b><br>")
		f.write("<span style=\"color:green\">Person patching: <b> TEAMMEMBER </b><br>" )
		kvmcount = 0
		for bu in sorted(bu_final):
			for h in host_tuple:
				if 'kvm' in h:
					if bu in h:
						kvmcount += 1
						print(f"{kvmcount}: {h[0]}")
						f.write(f"{kvmcount}: {h[0]}<br>")
	f.close()

def patch_gen(role,change_number,branch,date):
	# for local testing
	# mdfile = "/home/burger/work/fnb/public-wiki/scheduled_work/maintenance_slots/2021/" + date + "_test_page.md"
	# gitdir = "/home/burger/work/fnb/public-wiki/"

	# for prod
	mdfile = '/opt/flask/automated_admin/public-wiki/scheduled_work/maintenance_slots/2021/' + date + '_Infrastructure_Change_Weekend.md'
	gitdir = '/opt/flask/automated_admin/public-wiki/'

	bu_list = list()
	platform_list = list()
	git.initialize(branch,gitdir)

	file_creations.testMDfile(mdfile,role,change_number)
	dbcon = dbconnect.DBconnect(db,table)
	if dbcon.testconnect():
		print("connection established")
		if role == 'nonprod':
			nonprod_query = "SELECT * FROM {} where role != 'prod' and role != 'dr';".format(table)
			createLists(dbcon,nonprod_query,mdfile)

		elif role == 'prod':
			prod_query = "SELECT * FROM {} where role = 'prod' or role = 'dr';".format(table)
			createLists(dbcon,prod_query,mdfile)
	else:
		print(f"Connection to {db} failed.")

	file_creations.addExceptions(mdfile)
	git.pushup(branch,gitdir)
