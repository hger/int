#!/bin/env python

#First of we try to import all librarys needed.
#yum install python-scp will also install paramiko
try:
    import os, sys, socket, subprocess, logging, paramiko, shutil, time
except Exception, error:
    print "Error, missing required modules: " + str(error)
    sys.exit()

#All kind of variables
daServer = 'fileserver01.esss.lu.se'
daShare = 'ERPShare'
daLocalMount = '/mnt/erpshare'
hereBeFiles = '/mnt/erpshare/agrtest/Data Export/Sveorder_ut'
archiveOfFiles = '/mnt/erpshare/agrtest/Data Export/Sveorder_ut/sentOrders'
logFile = '/var/www/html/sendtoatea.log'
runFile = '/tmp/mountedfileserver.run'


allFilesInDir = []
allFoldersInDir = []

#Configuration of log level
logging.basicConfig(filename=logFile, level=logging.INFO)

#Remove old kerberos ticket for the host
def remove_kerberos_ticket():
    try:
        noTicket = subprocess.check_output(['/bin/kdestroy', '-A'])
        resultOut = 0, noTicket
#        print('got rid of ticket')
    except subprocess.CalledProcessError as e:
        resultOut = e.returncode, e.message
#        print('something failed with removing ticket')

def get_kerberos_ticket():
    krbName = (socket.gethostname().split('.')[0].upper() + '$')
    try:
        daTicket = subprocess.check_output(['/bin/kinit', krbName, '-k', '-t', '/etc/krb5.keytab'])
        resultOut = 0, daTicket
#        print('got ticket')
        #logging.info('got a new kerberos ticket')
    except subprocess.CalledProcessError as e:
        resultOut = e.returncode, e.message
 #       print('something failed with getting ticket')
        logging.error('got no kerberos ticket' + e.message)
        sys.exit('1')

def mount_server():
    out = subprocess.check_output(['/bin/klist'])
    myPrincipal = (out.split('\n'))[1].split()[2]
    try:
        daMount = subprocess.check_output(['/bin/mount', '-t', 'cifs', '-o', 'user=' + myPrincipal + ',sec=krb5', '//' + daServer + '/' + daShare, daLocalMount])
        resultOut = 0, daMount
#        print('mounted server')
        #logging.info('mounted filesevrver')
    except subprocess.CalledProcessError as e:
        resultOut = e.returncode, e.message
#        print('something failed with mounting server')
        logging.error('Could not mount server' + e.message)
        sys.exit('1')

def unmount_server(mntPoint):
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

#Send file using ssh to atea
def send_via_sftp(myFile):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect('ftp.atea.com', username='kalle', password='kalle')
        sftp = ssh.open_sftp()
        try:
            sftp.stat('/' + myFile)
#            print('file exists')
            logging.info('File ' + myFile + ' at ATEA already')
        except IOError:
#            print('copying file')
            sftp.put(hereBeFiles + '/' + myFile, '/' + myFile)
            logging.info('File ' + myFile + ' inplace at ftp.atea.com')
        ssh.close()
    except paramiko.SSHException:
#        print("Connection Error")
        logging.error('Connection Error when accessing ftp.atea.com')

def move_file_to_sentitems(myFile):
    shutil.move(hereBeFiles + '/' + myFile, archiveOfFiles + '/' + myFile)
    logging.info('Moved ' + myFile + ' to location on fileserver01')

if __name__ == '__main__':
    if not os.path.isfile(runFile):
        tmpfile = open(runFile, 'w')
        tmpfile.write('balle\n')
        tmpfile.close()
    else:
        sys.exit('1')
    unmount_server(daLocalMount)
    remove_kerberos_ticket()
    get_kerberos_ticket()
    mount_server()
    find_files(hereBeFiles)
    for alFiles in allFilesInDir:
        send_via_sftp(alFiles)
        move_file_to_sentitems(alFiles)
    unmount_server(daLocalMount)
    if os.path.isfile(runFile):
        os.remove(runFile)
