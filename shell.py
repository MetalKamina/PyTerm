import os
import subprocess

def shell(input):
	in_args = input.split(" ")
	if(in_args[0] == "cd" and len(in_args) > 1):
		try:
			os.chdir(in_args[1])
		except:
			return "Directory not found."
	if(in_args[0] == "ls"):
		return subprocess.check_output(input,shell=True).decode("utf-8")
	return str(os.getcwd())
