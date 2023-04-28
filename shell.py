import os
import subprocess

def shell(input):
	in_args = input.split(" ")
	if(in_args[0] == ""):
        	return str(os.getcwd())
	try:
		proc = subprocess.Popen(in_args,stdout=subprocess.PIPE)
		return proc.stdout.read().decode("utf-8")
	except Exception as e:
		return str(e)
	return str(os.getcwd())
