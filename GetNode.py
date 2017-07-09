import sys
import jenkins
import logging
import re
import os
import mysql.connector


PATH="D:\\JenkinsUtilities\\"
def get_Logger(loggerName,fileName):
	logger = logging.getLogger(loggerName)
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler(fileName)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	return logger



def main(argv):
	if len(argv) < 2:
		print "Incorrect Command format missing arguments"
		exit(-1)
	Environment=argv[0]
	Table_Name=argv[1]
	Log_File=PATH+Environment+"GetNode.log"
	logger=get_Logger("GetNode",Log_File);
	conn = mysql.connector.connect(host='172.16.0.26', port=3306, user='cwadmin', passwd='cwadmin', db='CI')
	cur = conn.cursor()
	cur_write = conn.cursor()
	cur.execute("SELECT NodeName,MonFolderLocation,WebSiteFolderLocation,MonBackupLocation,RemoteScriptLocation,WebSiteBackUpLocation,ComputerName,ApplicationName,WebSiteFolderName,PORT,RobotBackupPath FROM %s where branchname = '%s'" %(Table_Name,os.environ['BRANCH_NAME']))	
	
	row = cur.fetchall()
	if len(row) == 0:
		logger.debug("branch not hosted") 
		cur.execute("SELECT NodeName,MonFolderLocation,WebSiteFolderLocation,MonBackupLocation,RemoteScriptLocation,WebSiteBackUpLocation,ComputerName,ApplicationName,WebSiteFolderName,PORT FROM %s where OccupancyStatus = 0" %(Table_Name))
		row1 = cur.fetchall()
		if len(row1) == 0:
			print "No Staging Environment available"
			exit(1)

		else:
			update_query = "UPDATE %s SET OccupancyStatus = 1 , branchname = '%s' where ApplicationName = '%s' "  % (Table_Name,os.environ['BRANCH_NAME'],row1[0][7])
			cur_write.execute(update_query)
			conn.commit()
			conn.close()
			serverdetails = ";".join(row1[0])
			print serverdetails
	else:
		logger.debug("branch already hosted")
		update_query = "UPDATE %s SET OccupancyStatus = 1 , branchname = '%s' where ApplicationName = '%s' "  % (Table_Name,os.environ['BRANCH_NAME'],row[0][7])
		cur_write.execute(update_query)
		conn.commit()
		conn.close()
		serverdetails = ";".join(row[0])
		print serverdetails

if __name__ == '__main__':
	main(sys.argv[1:])
