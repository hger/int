#!/bin/env python

#First of we try to import all librarys needed.
#yum install python-scp will also install paramiko
try:
    import os, sys, socket, subprocess, logging, paramiko, shutil, time, ess_int_lib
except Exception, error:
    print "Error, missing required modules: " + str(error)
    sys.exit()

tempFile = '/tmp/mountedfileserver.run'

if not os.path.isfile(tempFile):
    tmpfile = open(tempFile, 'w')
    tmpfile.write('balle\n')
    tmpfile.close()
    print('now the integration is running')
else:
    print('Already running, now I die....')


if os.path.isfile(tempFile):
    os.remove(tempFile)
    print('now no more atea')
