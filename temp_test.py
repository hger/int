#!/bin/env python

#First of we try to import all librarys needed.
#yum install python-scp will also install paramiko
try:
    import os, sys, socket, subprocess, logging, paramiko, shutil, time, ess_int_lib
except Exception, error:
    print "Error, missing required modules: " + str(error)
    sys.exit()

ess_int_lib.set_logging_level('/tmp/sftp/hello.log')
logging.info('got a new kerberos ticket')
logging.error('lost my kerberos ticket')
