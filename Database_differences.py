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

def gitDiff(prev_commit_hash,curr_commit_hash,REPO_LOCATION):
	format = '--name-only'
	files = []
	g = git.Git(REPO_LOCATION)
	differ = g.diff('%s..%s' % (prev_commit_hash, curr_commit_hash), format, '--' ,REPO_LOCATION ).split("\n")
	for line in differ:
		if len(line):
			files.append(line)
	return files
def main(argv):
	if len(argv) < 1:
		print "Incorrect Command format missing arguments"
		exit(-1)
	REPO_LOCATION =argv[0]
	repo = git.Repo(REPO_LOCATION)
	commits_list = list(repo.iter_commits())
	curr_commit_hash = commits_list[0]
	prev_commit_hash = commits_list[1]
	changed_scripts=gitDiff(curr_commit_hash,prev_commit_hash,REPO_LOCATION)
	database_scripts=[]
	for file in changed_scripts:	
		if file.lower().find("database") >=0:	
			database_scripts.append(file)
	if len(database_scripts) >0:
		print "Database_Scripts_changed",database_scripts

if __name__ == '__main__':
	main(sys.argv[1:])