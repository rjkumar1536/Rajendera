import os
import paramiko
import sys

def isFileExists(sftp, path):
    try:
        sftp.stat(path)
        # print "hello"
    except IOError, e:
        # print str(e)
        if 'No such file' in str(e):
            return False
        raise
    else:
        return True

def main(argv):
    if len(argv) < 2:
        print "Incorrect Command format missing arguments"
        exit(-1)    
    REMOTE_SERVER_IP = argv[0]
    LOCK_FILE = argv[1]    
    k = paramiko.RSAKey.from_private_key_file("C:\cygwin64\home\.ssh\id_rsa")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect( hostname = REMOTE_SERVER_IP, username = "ciadmin", pkey = k )
    sftp = c.open_sftp()
    if isFileExists(sftp,LOCK_FILE):
        sftp.remove(LOCK_FILE)
    sftp.close()
    c.close()

if __name__ == '__main__':
    main(sys.argv[1:])