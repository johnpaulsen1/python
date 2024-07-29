#!/usr/bin/python3

import os
import subprocess
import shlex
from datetime import date, datetime

def getOScmdOutput(cmd):
	cmd_args = shlex.split(cmd)
	exec_cmd = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	raw_output = exec_cmd.communicate()[0]
	output = raw_output.decode("utf-8")
	return output.strip()
