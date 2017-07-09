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

def moveTree(sourceRoot, destRoot,sftp):
    if not isFileExists(sftp,destRoot):
        return False
    for path, dirs, files in os.walk(sourceRoot):
        relPath = os.path.relpath(path, sourceRoot)
        destPath = os.path.join(destRoot, relPath)
        if not isFileExists(sftp,destPath + "/"):
            sftp.mkdir(destPath)
        for file in files:
            print file
            destFile = os.path.join(destPath, file)
            if isFileExists(sftp,destFile):
                print "Skipping existing file: " + os.path.join(relPath, file)
                continue
            srcFile = os.path.join(path, file)
            sftp.put(srcFile, destFile)
    return True

def main(argv):
    if len(argv) < 3:
        print "Incorrect Command format missing arguments"
        exit(-1)    
    REMOTE_SERVER_IP = argv[0]
    REMOTE_SERVER_PATH = argv[1]    
    LOCAL_PATH = argv[2]
    k = paramiko.RSAKey.from_private_key_file("C:\cygwin64\home\.ssh\id_rsa")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect( hostname = REMOTE_SERVER_IP, username = "ciadmin", pkey = k )
    sftp = c.open_sftp()
    moveTree(LOCAL_PATH,REMOTE_SERVER_PATH,sftp)
    sftp.close()
    c.close()

if __name__ == '__main__':
    main(sys.argv[1:])
