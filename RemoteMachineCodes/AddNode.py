import os
import shutil
import sys
import logging 
import shutil
import subprocess


MON_FOLDER_LOCATION = ""
WEBSITE_FOLDER_LOCATION = ""
WEBSITE_FOLDER_NAME = ""
MON_BACKUP_LOCATION = ""
MON_FILEUP_NAME = "heartbeat_up.html"
MON_FILEDOWN_NAME = "heartbeat_down.html"
ROBOT_TXT_BACKUP_LOCATION = ""



def get_Logger(loggerName,fileName):
	logger = logging.getLogger(loggerName)
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler(fileName)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	return logger

current_directory = sys.path[0] + "/"
logger = get_Logger("Addnode",current_directory+"Addnode.log")



def copytree(src, dst, symlinks=False, ignore=None):
	for item in os.listdir(src):
		s = os.path.normpath(os.path.join(src, item))
		d = os.path.normpath(os.path.join(dst, item))
		if os.path.isdir(s):
			shutil.copytree(s, d, symlinks, ignore)
		else:
			shutil.copy2(s, d)

def clean_folder(path):
	for root, dirs, files in os.walk(path):
		for f in files:
			os.unlink(os.path.join(root, f))
		for d in dirs:
			shutil.rmtree(os.path.join(root, d))

def add_monfolder(monpath,monbackup_path):
	source = os.path.normpath(monbackup_path)
	logger.debug("Mon Backup Folder " + source)
	destination = os.path.normpath(monpath)
	logger.debug("Production Mon Folder " + destination)
	if not os.path.exists(destination):
		os.makedirs(destination)
	else:
		clean_folder(destination)
	logger.debug("source %s , Destination %s" %(source,destination))	
	copytree(source,destination)

def add_robot(robot_path,robot_backup_path):
	source = os.path.join(robot_backup_path,"robots.txt")
	destination = os.path.join(robot_path,"robots.txt")
	shutil.copy2(source, destination)	

def main(argv):
	if len(argv) < 5:
		logger.error("Incorrect Command format missing arguments")
		exit(-1)
	MON_FOLDER_LOCATION = argv[0]
	WEBSITE_FOLDER_LOCATION = argv[1]
	WEBSITE_FOLDER_NAME = argv[2]
	MON_BACKUP_LOCATION = argv[3]
	ROBOT_TXT_BACKUP_LOCATION = argv[4]
	robot_path = os.path.join(WEBSITE_FOLDER_LOCATION,WEBSITE_FOLDER_NAME)
	logger.info("robot_path is "+ robot_path)
	logger.info("robot_backuppath is "+ ROBOT_TXT_BACKUP_LOCATION)

	add_robot(robot_path,ROBOT_TXT_BACKUP_LOCATION)
	logger.info("Robot.txt added")
	add_monfolder(MON_FOLDER_LOCATION,MON_BACKUP_LOCATION)
	logger.info("Server add to LB")
	print "server added successfully"
	connections = 0
	while connections < 2000:
		connections = 0
		p1 = subprocess.Popen(["netstat", "-ano" ], stdout=subprocess.PIPE)
		output = p1.communicate()[0].split("\n")
		for line in output:
			if line.find(":80") > 0:
				connections = connections + 1	

if __name__ == '__main__':
	main(sys.argv[1:])