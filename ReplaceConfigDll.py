import os
import paramiko
import sys

def isFileExists(sftp, path):
    try:
        sftp.stat(path)
        # print "hello"
    except IOError, e:
        print str(e)
        if 'No such file' in str(e):
            return False
        raise
    else:
        return True



def replace(REMOTE_SERVER_WEB_CONFIG_PATH,LOCAL_WEB_CONFIG_PATH,sftp):
	if isFileExists(sftp,REMOTE_SERVER_WEB_CONFIG_PATH):
		print "hello world"
		sftp.remove(REMOTE_SERVER_WEB_CONFIG_PATH)
	
	sftp.put(LOCAL_WEB_CONFIG_PATH, REMOTE_SERVER_WEB_CONFIG_PATH)


def main(argv):
    if len(argv) < 5:
        print "Incorrect Command format missing arguments"
        exit(-1)    
    REMOTE_SERVER_IP = argv[0]
    REMOTE_SERVER_WEB_CONFIG_PATH = argv[1]    
    REMOTE_SERVER_DLL_PATH = argv[2]
    LOCAL_WEB_CONFIG_PATH = argv[3]
    LOCAL_DLL_PATH  = argv[4]

    k = paramiko.RSAKey.from_private_key_file("C:\cygwin64\home\.ssh\id_rsa")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect( hostname = REMOTE_SERVER_IP, username = "ciadmin", pkey = k )
    sftp = c.open_sftp()
    #replace(REMOTE_SERVER_WEB_CONFIG_PATH,LOCAL_WEB_CONFIG_PATH,sftp)
    replace(REMOTE_SERVER_DLL_PATH,LOCAL_DLL_PATH,sftp)
    # replaceDll(REMOTE_SERVER_DLL_PATH,LOCAL_DLL_PATH,sftp)
    sftp.close()
    c.close()


# python ReplaceConfigDll.py 172.16.0.15 D:/JenkinsUtilities/Production-DB/Testing/webConfig.txt D:/JenkinsUtilities/Production-DB/Testing/webConfig.txt D:/utils/CIcodes/GetNode.py D:/utils/CIcodes/GetNode.py

if __name__ == '__main__':
    main(sys.argv[1:])