import paramiko
import sys
import os
import mysql.connector
import logging




def get_Logger(loggerName,fileName):
	logger = logging.getLogger(loggerName)
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler(fileName)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	return logger

logger = get_Logger("GetNode","D:\\JenkinsUtilities\\Staging\\RemoteScripts\\Rollover.log")

def RollbackDatabase():
	conn = mysql.connector.connect(host='172.16.0.26', port=3306, user='cwadmin', passwd='cwadmin', db='CI')

	cur = conn.cursor()
	cur_write = conn.cursor()
	update_query = "UPDATE StagingWebsitePool SET OccupancyStatus = 0  where ApplicationName = '%s'" %  os.environ['APPLICATION_NAME']
	logger.debug(update_query) 
	cur_write.execute(update_query)
	conn.commit()
	conn.close()

def main(argv):
	if len(argv) < 9:
		print "Incorrect Command format missing arguments"
		logger.debug("Incorrect Command format missing arguments")
		exit(-1)	
	REMOTE_SCRIPT_LOCATION = argv[0]
	MON_FOLDER_LOCATION = argv[1]
	WEBSITE_FOLDER_LOCATION = argv[2]
	WEBSITE_FOLDER_NAME = argv[3]
	MON_BACKUP_LOCATION = argv[4]
	WEBSITE_BACKUP_LOCATION= argv[5]
	SERVER_IP = argv[6]
	ENVIRONMENT = argv[7]
	LOCK_FILE_LOCATION = argv[8]

	#logger.debug(REMOTE_SCRIPT_LOCATION,MON_BACKUP_LOCATION,WEBSITE_BACKUP_LOCATION,WEBSITE_FOLDER_NAME,MON_FOLDER_LOCATION)


	k = paramiko.RSAKey.from_private_key_file("C:\cygwin64\home\.ssh\id_rsa")
	c = paramiko.SSHClient()
	c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	c.connect( hostname = SERVER_IP, username = "ciadmin", pkey = k )
	stdin, stdout, stderr = c.exec_command('python %sRollback.py %s %s %s %s %s %s' %(REMOTE_SCRIPT_LOCATION,MON_FOLDER_LOCATION,WEBSITE_FOLDER_LOCATION,WEBSITE_FOLDER_NAME,MON_BACKUP_LOCATION,WEBSITE_BACKUP_LOCATION,LOCK_FILE_LOCATION ) )  # Non-blocking call
	exit_status = stdout.channel.recv_exit_status()          # Blocking call
	if exit_status == 0:
		print stdout.read()
		if ENVIRONMENT == 'staging':
			RollbackDatabase()
	else:
	    print stdout.read()
	    print stderr.read()
	    exit(-1)
	c.close()

if __name__ == '__main__':
	main(sys.argv[1:])

