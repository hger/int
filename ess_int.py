#!/bin/env python

#First of we try to import all librarys needed.
#yum install python-scp will also install paramiko
try:
    import os, sys, socket, subprocess, logging, paramiko, shutil, time
except Exception, error:
    print "Error, missing required modules: " + str(error)
    sys.exit()

#Configuration of log level (logging.INFO)
def set_logging_config(logFile):
    logging.basicConfig(filename=logFile, level=logging.INFO,
                        format='%(asctime)s,%(name)s,%(levelname)s,%(message)s',
                         datefmt='%Y-%m-%dT%H:%M:%S')
#                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
    logger = logging.getLogger(__name__)

#Remove old kerberos ticket for the host
def remove_kerberos_ticket():
    try:
        noTicket = subprocess.check_output(['/bin/kdestroy', '-A'])
        resultOut = 0, noTicket
    except subprocess.CalledProcessError as e:
        resultOut = e.returncode, e.message

#Get fresh new kerberos ticket for the host
def get_kerberos_ticket():
    krbName = (socket.gethostname().split('.')[0].upper() + '$')
    try:
        daTicket = subprocess.check_output(['/bin/kinit', krbName, '-k', '-t', '/etc/krb5.keytab'])
        resultOut = 0, daTicket
        logger.info('got a new kerberos ticket')
    except subprocess.CalledProcessError as e:
        resultOut = e.returncode, e.message
        logger.error('got no kerberos ticket' + e.message)
        sys.exit('1')

def mount_server(daServer, daShare, daLocalMount):
    out = subprocess.check_output(['/bin/klist'])
    myPrincipal = (out.split('\n'))[1].split()[2]
    try:
        daMount = subprocess.check_output(['/bin/mount', '-t', 'cifs', '-o', 'user=' + myPrincipal + ',sec=krb5', '//' + daServer + '/' + daShare, daLocalMount])
        resultOut = 0, daMount
        logger.info('mounted ' + daServer + ' at ' + daLocalMount)
    except subprocess.CalledProcessError as e:
        resultOut = e.returncode, e.message
#        print('something failed with mounting server')
        logger.error('Could not mount server' + e.message)
        sys.exit('1')

def unmount_server(daServer, mntPoint):
    while daServer in (subprocess.check_output(['mount', '-lt', 'cifs'])):
        subprocess.call(['umount', mntPoint])

def find_files(filePath):
    global allFilesInDir
    global allFoldersInDir
    entireDir = next(os.walk(filePath))
    allFilesInDir = entireDir[2]
    allFoldersInDir = entireDir[1]
    if allFilesInDir:
        return allFilesInDir
    if allFoldersInDir:
        return allFoldersInDir

#def create_unload_folder(filePath):
#    return time.strftime("%Y-%m-%d", time.localtime(os.stat(filePath).st_mtime))

#Send file using ssh to sftp server
def send_via_sftp(myFile, myHost, myUser, myPasswd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(myHost, username=myUser, password=myPasswd)
        sftp = ssh.open_sftp()
        try:
            sftp.stat('/' + myFile)
            logger.info('File ' + myFile + ' at ' + myHost + ' already')
        except IOError:
            sftp.put(hereBeFiles + '/' + myFile, '/' + myFile)
            logger.info('File ' + myFile + ' inplace at ' + myHost)
        ssh.close()
    except paramiko.SSHException:
        logger.error('Connection Error when accessing ' + myHost)

def move_file_to_sentitems(myFile, hereBeFiles, archiveOfFiles):
    shutil.move(hereBeFiles + '/' + myFile, archiveOfFiles + '/' + myFile)
    logger.info('Moved ' + myFile + ' to location at' + archiveOfFiles)

if __name__ == '__main__':
    sys.exit('0')
