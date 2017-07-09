import os
import git
import datetime
import logging
import sys
import traceback
import codecs
import string
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os import getenv
import subprocess
import pymysql
import traceback

LOCAL_DATABASE_HOST = '172.16.0.26'
LOCAL_USER = 'cwadmin'
LOCAL_PASSWORD = 'cwadmin'
MASTER_DATABASE = "CI"
DATABASE_PORT = 3306
ORIGIN_NAME = 'origin'

def get_Logger(loggerName,fileName):
	logger = logging.getLogger(loggerName)
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler(fileName)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	return logger

def PrintUnexpectedException(logger):
	exc_type ,exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	logger.error('EXCEPTION IN ({}, LINE {} ): {}'.format(filename, lineno, exc_obj))

logger = get_Logger("log_file","log_file.log")



def make_entry_database(Table_Name,branch_name,commit_hash,status,commit_msg,author): 
	insert_query = "insert into %s(BranchName, CommitHash, _status,updateddate,Commit_Message,Author_Name) values ('%s','%s','%s','%s','%s','%s') " % (Table_Name,branch_name,commit_hash,status,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7],commit_msg,author)
	return run_query(insert_query)

def update_database_entry(Table_Name,branch_name,commit_hash,status):
	update_query = "update %s set _status = '%s',updateddate = '%s' where  CommitHash = '%s' and BranchName = '%s'  " % (Table_Name,status,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7],commit_hash,branch_name)
	return run_query(update_query)

def run_query(query,host=LOCAL_DATABASE_HOST,user=LOCAL_USER,password=LOCAL_PASSWORD,database=MASTER_DATABASE):
	conn = pymysql.connect(host=host, port=DATABASE_PORT, user=user, passwd=password, db=database,autocommit=False)
	cur = conn.cursor()
	try:    
		logger.debug(query)		
		cur.execute(query)   
		conn.commit()
	except:
		PrintUnexpectedException(logger)
		traceback.print_exc()
		print "error occured in query ",query;
		conn.close()
		return False	
	conn.close()
	return True


def main(argv):
	if len(argv) < 6:
		print "Incorrect Command format missing arguments"
		exit(-1)
	CommitHash=argv[0].replace("'","")
	Author_Name=argv[1].replace("'","")
	Commit_Message=argv[2].replace("'","")
	Table_Name=argv[3].replace("'","")
	Query_Type=argv[4].replace("'","")
	Status=argv[5].replace("'","")
	BranchName=os.environ['BRANCH_NAME']
	try:
		if Query_Type=="insert":
			make_entry_database(Table_Name,BranchName,CommitHash,Status,Commit_Message,Author_Name)
		elif Query_Type=="update":
			update_database_entry(Table_Name,BranchName,CommitHash,Status)
	except:
		traceback.print_exc()
		

	
if __name__ == '__main__':
	main(sys.argv[1:])