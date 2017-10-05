#!/bin/env python

try:
    import os, sys, socket, subprocess, logging, paramiko, shutil, time, re, shutil, xml.dom.minidom
except Exception, error:
    print "Error, missing required modules: " + str(error)
    sys.exit()

invoiceNo = ''
companyId = ''
myLogFile = '/var/www/html/pagero.log'
runFile = '/tmp/mountedfileserver.run'
myMountPoint = '/mnt/erpshare/'
myServer = 'fileserver01.esss.lu.se'
mySharePoint = 'ERPShare'
myRemotePath = '/mnt/erpshare/agrprod/Svefakt/In/Efakturor/'
myLocalPath = '/sftp/pagero/home/from_pagero/'

class NoFilesException(Exception):
    pass

#Configuration of log level (logging.INFO)
def set_logging_config(logFile):
    logging.basicConfig(filename=logFile, level=logging.INFO,
                        format='%(asctime)s,%(name)s,%(levelname)s,%(message)s',
                         datefmt='%Y-%m-%dT%H:%M:%S')
#                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
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
#        logger.info('got a new kerberos ticket')
    except subprocess.CalledProcessError as e:
        resultOut = e.returncode, e.message
        logger.error('got no kerberos ticket' + e.message)
        sys.exit('1')

#Mount the server using a kerberos ticket for the host
def mount_server(daServer, daShare, daLocalMount):
    out = subprocess.check_output(['/bin/klist'])
    myPrincipal = (out.split('\n'))[1].split()[2]
    try:
        daMount = subprocess.check_output(['/bin/mount', '-t', 'cifs', '-o', 'user=' + myPrincipal + ',sec=krb5', '//' + daServer + '/' + daShare, daLocalMount])
        resultOut = 0, daMount
#        logger.info('mounted ' + daServer + ' at ' + daLocalMount)
    except subprocess.CalledProcessError as e:
        resultOut = e.returncode, e.message
        logger.error('Could not mount server' + e.message)
        sys.exit('1')

#Make sure that the mounted server is unmounted
def unmount_server(daServer, mntPoint):
    while daServer in (subprocess.check_output(['mount', '-lt', 'cifs'])):
        subprocess.call(['umount', mntPoint])

#Parse the actual xml file into memory
def parse_file(theFile):
    try:
        return xml.dom.minidom.parse(theFile)
    except IOError, error:
        logger.error('File not found: ' + str(error))
        sys.exit()
    except xml.parsers.expat.ExpatError, error:
        logger.error('Parser error: ' + str(error))
        raise Exception('xml file parse error')


#Parse an efaktura xml file and return the invoice number
def get_invoiceNo(xml_in):
    try:
        invoiceNo = xml_in.getElementsByTagName("ID")[0].firstChild.nodeValue
        return invoiceNo
    except IndexError, error:
        logger.error('ID tag not found: ' + str(error))
        raise Exception('ID tag in xml missing')

#Parse an efaktura xml file and return the dir 
def get_companyId(xml_in):
    try:
        company = xml_in.getElementsByTagName("cac:SellerParty")[0]
        companyId = company.getElementsByTagName("cac:CompanyID")[0].firstChild.nodeValue
        return  companyId
    except IndexError, error:
        logger.error('CompanyID tag not found: ' + str(error))
        raise Exception('CompanyID tag in xml missing')

#List files and folders in a specified folder
def find_files(filePath):
    if os.path.exists(filePath):
        entireDir = next(os.walk(filePath))
        allFilesInDir = entireDir[2]
        if allFilesInDir:
            return allFilesInDir
        else:
            raise NoFilesException()
    else:
        raise Exception('The path is wrong: ' + filePath)

#Locate every file connected to the invoice number, create a folder for the attachement and
#then move the invoice file and folder with attachements to the server
def move_files_to_server(myList):
    for files in myList:
        try:
            if files.startswith('invoice_'):
                xml = parse_file(myLocalPath + files)
                logger.info(files + ', invoiceNo:, ' + get_invoiceNo(xml) + ', companyId:, ' + get_companyId(xml))
                invName = (files.split('.')[0])
                if os.path.exists('/tmp/' + invName):
                    shutil.rmtree('/tmp/' + invName)
                os.makedirs('/tmp/' + invName)
                invNumber = re.findall(r'\d+', files)[0]
                for listoffiles in myList:
                    if invNumber in listoffiles and not listoffiles.startswith('invoice_'):
                        os.rename(myLocalPath + listoffiles, '/tmp/' + invName + '/' + listoffiles)
                print(myLocalPath + files, myRemotePath + files)
                shutil.move(myLocalPath + files, myRemotePath + files)
                print('/tmp/' + invName, myRemotePath + invName)
                shutil.move('/tmp/' + invName, myRemotePath + invName)
        except Exception, error:
            logger.error('This went wrong: ' + str(error))


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
    if not os.path.isfile(runFile):
        tmpfile = open(runFile, 'w')
        tmpfile.write('isworking\n')
        tmpfile.close()
    else:
        sys.exit('1')
    set_logging_config(myLogFile)
    logger = logging.getLogger(__name__)
    unmount_server(myServer, myMountPoint)
    remove_kerberos_ticket()
    get_kerberos_ticket()
    mount_server(myServer, mySharePoint, myMountPoint)
    try:
        move_files_to_server(find_files(myLocalPath))
    except NoFilesException:
        pass
    except Exception, error:
        logger.error('The error: ' + str(error))
    unmount_server(myServer, myMountPoint)
    if os.path.isfile(runFile):
        os.remove(runFile)
#    logger.info('ran the script')

