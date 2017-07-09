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
import time
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os import getenv
import subprocess



def main(argv):
	if len(argv) < 1:
		print "Incorrect Command format missing arguments"
		exit(-1)
	file_path=argv[0]+"Email_Recipients.txt"
	EMAIL=""
	recipient=[]
	with open(file_path,"r") as text:
		for line in text:
			if line.startswith('Email'):
				EMAIL=line.split(":")[1]
			if line.startswith('Recipients'):
				recipient=line.split(":")[1].split(",")
	gmail_user = "checks.carwale@gmail.com"
	gmail_pwd = "arrow1851"
	FROM = "checks.carwale@gmail.com"
	TO = recipient if type(recipient) is list else [recipient]
	SUBJECT = "Changes in database "
	TEXT = "  please check files. It is CRITICAL"


	msg = MIMEMultipart()
	msg['From']=FROM
	msg['To']=COMMASPACE.join(TO)
	msg['Date']=formatdate(localtime=True)
	msg['Subject'] = SUBJECT
	msg.attach(MIMEText(TEXT))


	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(gmail_user, gmail_pwd)
		server.sendmail(FROM, recipient, msg.as_string())
		server.close()
		print 'successfully sent the mail'
	except Exception as e:
  		print e
		print "failed to send mail"

if __name__ == '__main__':
	main(sys.argv[1:])