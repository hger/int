#!/bin/env python

import os
import sys
import shutil
import xml.dom.minidom
import logging
import re
import argparse

myEnvs = ['prod', 'test']

parser = argparse.ArgumentParser(description='Select which environement')
parser.add_argument('env', metavar='prod', type=str, help='either prod or test')

args = parser.parse_args()


print(str(args.env))


myStr = str(args.env)

if any(x in myStr for x in myEnvs):
    print('kalle')
else:
    print('fail')

sys.exit()

logging.basicConfig()
logger = logging.getLogger('hej')
#myRemotePath = '/mnt/erpshare/agrtest/Svefakt/In/Efakturor/'
myRemotePath = '/tmp/fileserver/'
#myLocalPath = '/sftp/pagerotest/home/from_pagero/'
myLocalPath = '/tmp/sftp/'

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
            raise Exception('folder is empty')
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

try:
    move_files_to_server(find_files(myLocalPath))
except Exception, error:
    logger.error('The error: ' + str(error))