#!/usr/bin/python3

import subprocess
import os
import sys

os.chdir("../")
installdir = os.getcwd()

# Check the path for the python executable:
command = "which python3 > /tmp/pythonpath.txt"
subprocess.call(command, shell=True)
pythonpathfile = open("/tmp/pythonpath.txt")
pythonpath = pythonpathfile.readline().strip()
print(pythonpath)

if pythonpath!="/usr/bin/python3":
	print("Updating python executable locations")
	filelist = os.listdir()
	for name in filelist:
		if name[-3:] == ".py":
			pyfile = open(name,'r')
			pyout = open(name+"tmp",'w')
			pyfile.readline()
			pyout.write("#!"+pythonpath+"\n")
			for line in pyfile.readlines():
				pyout.write(line)
			os.remove(name)
			os.rename(name+"tmp",name)
else:
	print("Checked python executable locations")

# Make the files executable
print("Setting executable file permissions")
command = "chmod +x *.py"
subprocess.call(command, shell=True)

# Prompt user to update the path variable if required
command = "export PATH=$PATH:"+installdir
print("To make FURdb available in a current terminal session use the command:")
print(command)

# Prompt the user to update the path variable is desired
print("\nTo make the above change persistant the above line needs to be added to ~/.bashrc (if using a bash shell)")
if os.path.exists(os.path.expanduser("~/.bashrc")):
	print(".bashrc file found do you want this file updating? (y/N)")
	usrin = input('(default N):')
	if usrin.upper()=="Y":
		bashrc = open(os.path.expanduser("~/.bashrc"),'a')
		bashrc.write("\n\n")
		bashrc.write("# Added by FURdb install.py script to update file path\n")
		bashrc.write("# To reverse this change delete or comment out the following line\n")
		bashrc.write(command+"\n")
		print(".bashrc file has been updated, note changes will only take effect in new terminal sessions not current sessions.")
	else:
		sys.exit()
