import os
import shutil
import sys
import logging
import time
from shutil import copyfile
import subprocess

def get_Logger(loggerName,fileName):
	logger = logging.getLogger(loggerName)
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler(fileName)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	return logger


MON_FOLDER_LOCATION = ""
WEBSITE_FOLDER_LOCATION = ""
WEBSITE_FOLDER_NAME = ""
MON_BACKUP_LOCATION = ""
WEBSITE_BACKUP_LOCATION = ""
MON_FILEUP_NAME = "heartbeat_up.html"
MON_FILEDOWN_NAME = "heartbeat_down.html"
MAX_BACKUPS = 5
IGNORE_PATHS = ["grpc_csharp_ext.x64.dll","ISAPI_Rewrite_x64.dll"]
# utility_path = sys.path[0]
current_directory = sys.path[0] + "/"
logger = get_Logger("Rollback",current_directory+"Rollback.log")


def removeEmptyFolders(path):
    if not os.path.isdir(path):
        return
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                removeEmptyFolders(fullpath)
    files = os.listdir(path)
    if len(files) == 0:
        print "Removing empty folder:", path
        os.rmdir(path)

def clean_folder(path,ignore_paths):
    for root, dirs, files in os.walk(path):
        for f in files:
            sourceFile=os.path.join(root, f)
            print f
            if f not in ignore_paths:
                if os.path.exists(sourceFile):
                    os.unlink(sourceFile)
    removeEmptyFolders(path)

def down_mon(monpath):			
	source = os.path.normpath(os.path.join(monpath,MON_FILEUP_NAME))
	destination = os.path.normpath(os.path.join(monpath,MON_FILEDOWN_NAME))
	logger.debug("Removing server from production")
	if os.path.exists(destination):
		logger.debug("Already mon down")
	if os.path.exists(source):
		os.rename(source,destination)
		connections = 10000
		while connections > 40:
			connections = 0
			p1 = subprocess.Popen(["netstat", "-ano" ], stdout=subprocess.PIPE)
			output = p1.communicate()[0].split("\n")
			for line in output:
				if line.find(":80") > 0:
					connections = connections + 1

def rollback(path,folder_name,website_backup_location,ignore_paths):
	logger.debug("Rolling Back website " + folder_name)
	if not os.path.exists(website_backup_location):
		logger.error("Backup does not exist on path " + website_backup_location)
		print "Backup does not exist " + website_backup_location
	clean_folder(os.path.join(path, folder_name),ignore_paths)
	time.sleep(20)
	copytree(os.path.join(website_backup_location,folder_name + '_' + str(MAX_BACKUPS)),os.path.join(path, folder_name))
	shutil.rmtree(os.path.join(website_backup_location,folder_name + '_' + str(MAX_BACKUPS)))
	for i in xrange(MAX_BACKUPS, 0, -1):
		if os.path.exists(os.path.join(website_backup_location,folder_name + '_' + str(i-1))):
			os.rename(os.path.join(website_backup_location,folder_name + '_' + str(i-1)),os.path.join(website_backup_location,folder_name + '_' + str(i)))


def copytree(sourceRoot, destRoot):
    for path, dirs, files in os.walk(sourceRoot):
        relPath = os.path.relpath(path, sourceRoot)
        destPath = os.path.join(destRoot, relPath)
        if not os.path.exists(destPath):
            os.makedirs(destPath)
        for file in files:
            sourceFile=os.path.join(path, file)
            destFile = os.path.join(destPath, file)
            if not os.path.exists(destFile):
                copyfile(sourceFile, destFile)

def main(argv):
	if len(argv) < 6:
		logger.error("Incorrect Command format missing arguments")
		exit(-1)
	MON_FOLDER_LOCATION = argv[0]
	WEBSITE_FOLDER_LOCATION = argv[1]
	WEBSITE_FOLDER_NAME = argv[2]
	MON_BACKUP_LOCATION = argv[3]
	WEBSITE_BACKUP_LOCATION = argv[4]
	LOCK_FILE_LOCATION = argv[5]
	down_mon(MON_FOLDER_LOCATION)
	if os.path.exists(LOCK_FILE_LOCATION):
		rollback(WEBSITE_FOLDER_LOCATION,WEBSITE_FOLDER_NAME,WEBSITE_BACKUP_LOCATION,IGNORE_PATHS)

if __name__ == '__main__':
	main(sys.argv[1:])