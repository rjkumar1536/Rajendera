import os
import shutil
import sys
import logging
import time
import subprocess

MON_FOLDER_LOCATION = ""
WEBSITE_FOLDER_LOCATION = ""
WEBSITE_FOLDER_NAME = ""
MON_BACKUP_LOCATION = ""
WEBSITE_BACKUP_LOCATION = ""
MON_FILEUP_NAME = "heartbeat_up.html"
MON_FILEDOWN_NAME = "heartbeat_down.html"
MAX_BACKUPS = 5


def get_Logger(loggerName,fileName):
	logger = logging.getLogger(loggerName)
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler(fileName)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s\n')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	return logger

current_directory = sys.path[0] + "/"
logger = get_Logger("RemoveNode",current_directory + "RemoveNode.log")

def make_backup(path,folder_name,website_backup_location):
	logger.info("Creating Backup")
	destination = os.path.normpath(os.path.join(website_backup_location,folder_name + '_' + str(MAX_BACKUPS)))
	logger.info("Backup destination " + destination)
	if os.path.exists(os.path.normpath(destination)):
		rotate_backup(website_backup_location,folder_name,MAX_BACKUPS)
		logger.info("Creating Backup destination " + destination)
	os.makedirs(os.path.normpath(destination))
	logger.info("Copying into Backup " + destination)
	copytree(os.path.normpath(os.path.join(path, folder_name)),os.path.normpath(destination))
	return 


def rotate_backup(website_backup_location,folder_name,num_of_backups):
	logger.debug("rotating backup " + str(num_of_backups))
	source = os.path.normpath(os.path.join(website_backup_location,folder_name + '_' + str(num_of_backups)))
	if num_of_backups == 0: 
		if os.path.exists(source):
			shutil.rmtree(source)
			time.sleep(30)
		logger.debug("rotated backup " + str(num_of_backups))
		return
	destination = os.path.join(website_backup_location,folder_name + '_' + str(num_of_backups - 1) )	
	if os.path.exists(destination):
		rotate_backup(website_backup_location,folder_name,num_of_backups-1)
		time.sleep(10)
	os.rename(os.path.normpath(source),os.path.normpath(destination))
	logger.debug("rotated backup " + str(num_of_backups))
	return 

def copytree(src, dst, symlinks=False, ignore=None):
	for item in os.listdir(os.path.normpath(src)):
		s = os.path.normpath(os.path.join(src, item))
		d = os.path.normpath(os.path.join(dst, item))
		if os.path.isdir(s):
			shutil.copytree(s, d, symlinks, ignore)
		else:
			shutil.copy2(s, d)

def down_mon(monpath):			
	source = os.path.normpath(os.path.join(monpath,MON_FILEUP_NAME))
	destination = os.path.normpath(os.path.join(monpath,MON_FILEDOWN_NAME))
	logger.debug("Removing server from production")
	if os.path.exists(destination):
		logger.debug("Already mon down")
	if os.path.exists(source):
		os.rename(source,destination)



def main(argv):
	if len(argv) < 5:
		logger.error("Incorrect Command format missing arguments")		
		exit(1)
	MON_FOLDER_LOCATION = argv[0]
	WEBSITE_FOLDER_LOCATION = argv[1]
	WEBSITE_FOLDER_NAME = argv[2]
	MON_BACKUP_LOCATION = argv[3]
	WEBSITE_BACKUP_LOCATION = argv[4]
	LOCK_FILE_LOCATION = argv[5]
	down_mon(MON_FOLDER_LOCATION)
	logger.debug("Server Removed from Production")
	if not os.path.exists(LOCK_FILE_LOCATION):
		make_backup(WEBSITE_FOLDER_LOCATION,WEBSITE_FOLDER_NAME,WEBSITE_BACKUP_LOCATION)
		file = open(LOCK_FILE_LOCATION,"w")
		file.close()
	connections = 0
	while connections > 40:
		connections = 0
		p1 = subprocess.Popen(["netstat", "-ano" ], stdout=subprocess.PIPE)
		output = p1.communicate()[0].split("\n")
		for line in output:
			if line.find(":80") > 0:
				connections = connections + 1

# command format python scriptname.py monfilelocation , website_folder_location, website_folder_name, mon_backup_location
if __name__ == '__main__':
	main(sys.argv[1:])


