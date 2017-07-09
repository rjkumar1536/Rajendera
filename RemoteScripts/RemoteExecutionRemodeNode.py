import paramiko
import sys
import os


def main(argv):
	if len(argv) < 8:
		print "Incorrect Command format missing arguments"
		exit(-1)	
	REMOTE_SCRIPT_LOCATION = argv[0]
	MON_FOLDER_LOCATION = argv[1]
	WEBSITE_FOLDER_LOCATION = argv[2]
	WEBSITE_FOLDER_NAME = argv[3]
	MON_BACKUP_LOCATION = argv[4]
	WEBSITE_BACKUP_LOCATION= argv[5]
	SERVER_IP = argv[6]
	BACKUP_LOCK_FILE = argv[7]

	k = paramiko.RSAKey.from_private_key_file("C:\cygwin64\home\.ssh\id_rsa")
	c = paramiko.SSHClient()
	c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	c.connect( hostname = SERVER_IP, username = "ciadmin", pkey = k )
	stdin, stdout, stderr = c.exec_command('python %sRemoveNode.py %s %s %s %s %s %s' %(REMOTE_SCRIPT_LOCATION, MON_FOLDER_LOCATION, WEBSITE_FOLDER_LOCATION, WEBSITE_FOLDER_NAME, MON_BACKUP_LOCATION, WEBSITE_BACKUP_LOCATION, BACKUP_LOCK_FILE ) )  # Non-blocking call
	exit_status = stdout.channel.recv_exit_status()          # Blocking call
	if exit_status == 0:
		print stdout.read()
	else:
	    print stdout.read()
	    print stderr.read()
	    exit(-1)
	c.close()	



if __name__ == '__main__':
	main(sys.argv[1:])

