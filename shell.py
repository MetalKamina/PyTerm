import os
import subprocess

def shell(input):
	if(input == ""):
		return str(os.getcwd())
	in_args = input.split(" ")
	try:
		proc = subprocess.Popen(in_args,stdout=subprocess.PIPE)
		return proc.stdout.read().decode("utf-8")
	except Exception as e:
		return str(e)
	return str(os.getcwd())
