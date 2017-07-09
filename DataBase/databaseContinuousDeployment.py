import re 
import pymysql
import logging
import os
import git
import datetime
import logging
import sys
import traceback
import codecs
import string
import smtplib
import subprocess
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os import getenv
import config
import importlib
from collections import defaultdict

LOCAL_DATABASE_HOST = config.LOCAL_DATABASE_HOST
LOCAL_USER = config.LOCAL_USER
LOCAL_PASSWORD = config.LOCAL_PASSWORD
MASTER_DATABASE = config.MASTER_DATABASE
DATABASE_PORT = 3306
ORIGIN_NAME = config.ORIGIN_NAME
DATABASES = config.DATABASES


COUNTER=1
MERGE_BASE_COMMIT_HASH=""
CURRENT_COMMIT_HASH=""
CURRENT_BRANCH=""
#--------------------------------------logging related functions---------------------------------------#
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
logger.info("\n_________________\n")

#-------------------------------------database related functions-------------------------------------------#

def make_entry_database(branch_name,commit_hash,status,merge_commit_hash,count=COUNTER): 
	insert_query = "insert into CIDatabaseChangeHistory(BranchName, CommitHash, _status, updateddate,COUNTER,MERGE_BASE_COMMIT_HASH,Author_Name) values ('%s','%s','%s','%s',%s,'%s','%s') " % (branch_name,commit_hash,status,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7],count,merge_commit_hash,AUTHOR)
	return run_query(insert_query)

def Update_ScriptChange_db(status,curr_commit_hash,curr_branch,schema_name,script_name,count=COUNTER):
	if script_name.lower().find(LOCATION.lower())!=-1:
		script_name=string.replace(script_name,LOCATION+'/',"")
	if script_name.lower().find(LOCATION.lower())!= -1:
		script_name=string.replace(script_name,LOCATION+'/',"")
	update_query = "update CIScriptChangeHistory set _status = '%s',updateddate = '%s' where  CommitHash = '%s' and BranchName = '%s' and COUNTER = %s and ScriptName='%s' " % (status,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7],curr_commit_hash,curr_branch,count,script_name)
	return run_query(update_query)

def make_Script_Change_Entry(status,curr_commit_hash,curr_branch,schema_name,script_name,count=COUNTER):
	insert_query = "insert into CIScriptChangeHistory  values ('%s','%s','%s','%s','%s','%s','%s') " % (status,curr_commit_hash,curr_branch,schema_name,script_name,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7],count)
	return run_query(insert_query)

def update_database_entry(branch_name,commit_hash,status,count=COUNTER):
	update_query = "update CIDatabaseChangeHistory set _status = '%s',updateddate = '%s' where  CommitHash = '%s' and BranchName = '%s' and COUNTER = %s " % (status,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7],commit_hash,branch_name,count)
	return run_query(update_query)

def get_COUNTER(curr_commit_hash,branch_name):
	conn = pymysql.connect(host=LOCAL_DATABASE_HOST, port=DATABASE_PORT, user=LOCAL_USER, passwd=LOCAL_PASSWORD, db=MASTER_DATABASE)
	query = "select COUNTER from CIDatabaseChangeHistory where BranchName = '%s' and CommitHash = '%s' order by COUNTER desc " % (branch_name,curr_commit_hash)
	cur=conn.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	conn.close()
	if rows == None:
		return 1
	if len(rows) == 0:
		return 1
	else:
		return rows[0][0] + 1
	return 
#---------------------------------------------git related functions---------------------------------------#

def gitCheckout(commit_hash):
 	g = git.Git(LOCATION)
 	g.checkout(commit_hash)

def get_sha_current(repo):
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo).decode('ascii').strip()
    return sha

def gitMergeBase(curr_branch,base_branch):
	g = git.Git(LOCATION)
	commitHash = g.merge_base(curr_branch,base_branch)
	return commitHash
	

def gitDiff(prev_commit_hash,curr_commit_hash,path):
	format = '--name-only'
	files = []
	g = git.Git(LOCATION)
	differ = g.diff('%s..%s' % (prev_commit_hash, curr_commit_hash), format, '--' ,path ).split("\n")
	for line in differ:
		if len(line):
			files.append(line)
	return files
#-------------------------------query related functions-----------------------------------------#

def run_query(query,host=LOCAL_DATABASE_HOST,user=LOCAL_USER,password=LOCAL_PASSWORD,database=MASTER_DATABASE):
	conn = pymysql.connect(host=host, port=DATABASE_PORT, user=user, passwd=password, db=database,autocommit=False)
	cur = conn.cursor()
	try:    
		logger.debug(query)		
		cur.execute(query)   
		conn.commit()
	except:
		PrintUnexpectedException(logger)
		print "error occured in query ",query;
		conn.close()
		return False	
	conn.close()
	return True



def get_SQLContent_From_File(filename,database,commit_hash,branch_name,count,directory_path=""):
	length=len(directory_path)
	if length>0:
		path =directory_path+"/"+filename
	else:
		path=filename
	query=""
	if os.path.isfile(path):
		if path.find("\n"):
			path=path.replace("\n"," ")		
		with open(path, 'r') as f:
			query = " ".join(f.readlines())
		query=query.replace("\n"," ")
		query=query.replace("DELIMITER ;;"," ")
		query=query.replace("DELIMITER $$"," ")
		query=query.replace("$$"," ")
		query=query.replace(";;"," ")

		query=query.replace("DELIMITER ;"," ")
	return query

def convert_object_script(script_content,object_type,database,object_name):
		m = re.search("ALGORITHM = UNDEFINED", script_content,re.MULTILINE)
		if m != None:
			script_content =  script_content[:m.start()] + script_content[m.end():]
		m = re.search("DEFINER=`[^`]*`@`[^`]*`", script_content,re.MULTILINE)
		if m != None:
			script_content =  script_content[:m.start()] + script_content[m.end():] 
		m = re.search("SQL SECURITY DEFINER", script_content,re.MULTILINE)
		if m != None:
			script_content =  script_content[:m.start()] + script_content[m.end():]
		return  script_content 	


def get_changed_scripts(check,files,database):
	scripts=[]
	for file in files:	
		if file.lower().find("revert_scripts/") == -1:
			if file.lower().find(database.lower()) >=0:
				if file.lower().find("procedure") >=0:
					scripts.append(file)
	return scripts
def run_script(script,commit_hash,branch_name,database,count):
	if not make_Script_Change_Entry("IN PROGRESS",commit_hash,branch_name,database,script,count):
		return False
	script_content = get_SQLContent_From_File(script,database,commit_hash,branch_name,count,LOCATION)

	if len(script_content) >0:
		script_content = convert_object_script(script_content,script.split("/")[2],database,script.split("/")[-1].split(".")[0])
		if not run_query(script_content,host=DATABASES[database]['host'],user=DATABASES[database]['user'],password=DATABASES[database]['password'],database=database):
			logger.error("there is some error while executing script")
			Update_ScriptChange_db("ABORTED",commit_hash,branch_name,database,script,count)
			return False
		if not Update_ScriptChange_db("COMPLETED",commit_hash,branch_name,database,script,count):
		  return False

	return True


def get_prev_scripts(curr_branch=CURRENT_BRANCH,curr_commit_hash=CURRENT_COMMIT_HASH):
	conn = pymysql.connect(host=LOCAL_DATABASE_HOST, port=DATABASE_PORT, user= LOCAL_USER,passwd=LOCAL_PASSWORD, db=MASTER_DATABASE)
	query = "select ScriptName from CIScriptChangeHistory where BranchName = '%s'  and _status = 'COMPLETED'  " % (curr_branch)
	cur=conn.cursor()
	logger.debug(query)
	cur.execute(query)
	data =cur.fetchall()
	COLUMN=0
	rows=[elt[COLUMN] for elt in data]
	conn.close()
	return rows 

	
def IsAlreadyDeployed(path,database):
	conn = pymysql.connect(host=DATABASES[database]['host'], port=DATABASE_PORT, user=DATABASES[database]['user'], passwd=DATABASES[database]['password'], db=database)
	obj_name=path.split("/")[-1].replace(".sql","")
	query="SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_TYPE='PROCEDURE'  AND ROUTINE_NAME='%s' AND ROUTINE_SCHEMA='%s' "%(obj_name,database)
	cur=conn.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	conn.close()
	if rows == None:
		return False
	if len(rows) == 0:
		return False
	else:
		return True
	return True

def  get_merge_base(curr_branch,base_branch):
	return gitMergeBase(curr_branch,base_branch)
	# conn = pymysql.connect(host=LOCAL_DATABASE_HOST, port=DATABASE_PORT, user=LOCAL_USER, passwd=LOCAL_PASSWORD, db=MASTER_DATABASE)
	# query = "select MERGE_BASE_COMMIT_HASH from CIDatabaseChangeHistory  order by updateddate desc " 
	# cur=conn.cursor()
	# cur.execute(query)
	# rows = cur.fetchall()
	# conn.close()
	# if rows == None or len(rows) == 0:
	# 	return gitMergeBase(curr_branch,base_branch)
	# else:
	# 	print "from table"
	# 	return rows[0][0]
	# return    
def send_email(text):
	print text
	EMAIL=""
	recipient=[]
	file_path=LOCATION+"/"+"Email_Recipients.txt"
	print "In send mail1"
	with open(file_path,"r") as file:
		for line in file:
			if line.startswith('Email'):
				EMAIL=line.split(":")[1]
			if line.startswith('Recipients'):
				print line
				recipient=line.split(":")[1].split(",")
	print EMAIL
	print recipient
	gmail_user = "checks.carwale@gmail.com"
	gmail_pwd = "arrow1851"
	FROM = "checks.carwale@gmail.com"
	TO = recipient if type(recipient) is list else [recipient]
	SUBJECT = "inconsistency in database"
	TEXT = str(text)
	print TEXT

	# Prepare actual message
	msg = MIMEMultipart()
	msg['From']=FROM
	msg['To']=COMMASPACE.join(TO)
	msg['Date']=formatdate(localtime=True)
	msg['Subject'] = SUBJECT

	print "In send mail"

	try:
		msg.attach(MIMEText(TEXT))
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(gmail_user, gmail_pwd)
		server.sendmail(FROM, TO, msg.as_string())
		server.close()
		print 'successfully sent the mail'
	except:
		print "failed to send mail"

def main(argv):
	global AUTHOR
	global LOCATION
	if len(argv) < 3:
		print "Incorrect Command format missing arguments"
		exit(-1)
	CURRENT_BRANCH=argv[0]
	base_branch="origin/"+argv[1]
	LOCATION=argv[2]


	# CURRENT_COMMIT_HASH=get_sha_current(LOCATION)
	repo = git.Repo(LOCATION)
	commits_list = list(repo.iter_commits())
	commit = commits_list[0]
	CURRENT_COMMIT_HASH=str(commit).split(" ")[0]
	AUTHOR=str(commit.author)
	MERGE_BASE_COMMIT_HASH = get_merge_base(CURRENT_COMMIT_HASH,base_branch)
	print MERGE_BASE_COMMIT_HASH
	files = gitDiff(CURRENT_COMMIT_HASH,MERGE_BASE_COMMIT_HASH,LOCATION)
	COUNTER = get_COUNTER(CURRENT_COMMIT_HASH,CURRENT_BRANCH)
	make_entry_database(CURRENT_BRANCH,CURRENT_COMMIT_HASH,"Started",MERGE_BASE_COMMIT_HASH,COUNTER)	
	prev_deployed_scripts=get_prev_scripts(CURRENT_BRANCH,CURRENT_COMMIT_HASH)
	try:
		for database in DATABASES:
			current_changed_scripts_db=get_changed_scripts(0,files,database)
			print current_changed_scripts_db
			if len(current_changed_scripts_db) == 0:
				logger.info("No database change detected for branch %s and commit %s" % (CURRENT_BRANCH,CURRENT_COMMIT_HASH))
			else:
				logger.info("database files changed in branch %s" %(CURRENT_BRANCH))
			string="https://github.com/carwale/CIDemoRepository/compare/"+MERGE_BASE_COMMIT_HASH+"...carwale:"+CURRENT_COMMIT_HASH
			print "Go to.....::\n",string,"\n"
			scripts=[]
			

			for path in current_changed_scripts_db:
				if  not path in(s for s in prev_deployed_scripts):
					if not IsAlreadyDeployed(path,database):		
						scripts.append(path)
					else:
						print "The procedure already exists at the database",path,"\n"
						# exit(-1)
				else:
					print "Its already deployed in current branch",path,"\n"
			review_scripts=[]
			for file in scripts:
				review_scripts.append(LOCATION+"/"+file)
			Dict=defaultdict(list)
			Dict[database]=review_scripts
			reviewer=importlib.import_module("Review")
			Result = reviewer.GetInput(Dict)
			MailContent=""
			for k,v in Result.iteritems(): 
				print   
				filename='"file" : %s'%k
				MailContent=MailContent+filename
				index=1
				MailContent+= '\n"Errors" : \n'
				for warnings in v:
					RelatedReview= "(%d) %s"%(index,warnings)
					MailContent=MailContent+RelatedReview+"\n"
					index=index+1
			print MailContent
			send_email(MailContent)
			# print "Sripts Deploying now are::",scripts
			# for path in scripts:
			# 	if run_script(path,CURRENT_COMMIT_HASH,CURRENT_BRANCH,database,COUNTER):
			# 		logger.info("%s Execution Successfully" % (path) )
			# 		print("%s Execution Successfull " % (path) )
										
			# 	else:
			# 		logger.info("%s Execution Unsuccessfull " % (path))
			# 		print("%s Execution Unsuccessfull" % (path))
			# 		update_database_entry(CURRENT_BRANCH,CURRENT_COMMIT_HASH,"FAILED")		
			# 		exit(-1)		
			# 		break
							
		is_execution_successful=update_database_entry(CURRENT_BRANCH,CURRENT_COMMIT_HASH,"COMPLETED",COUNTER)
	except:
		PrintUnexpectedException(logger)
		is_execution_successful=update_database_entry(CURRENT_BRANCH,CURRENT_COMMIT_HASH,"FAILED")		
		exit(-1)	
	if is_execution_successful:
		logger.info("Successfully updated in database")
	else:
		logger.info("Unable to make entry in database")
		exit(-1)

if __name__ == '__main__':
	main(sys.argv[1:])


