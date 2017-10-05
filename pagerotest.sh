#!/bin/bash

#mount -t cifs -o user='SFTP01$@ESSS.LU.SE',sec=krb5 --verbose //fileserver01.esss.lu.se/ERPShare /mnt/erpshare

#First check if we are already running
if ! [ -f /tmp/mountedfileserver.run ]; then
    touch /tmp/mountedfileserver.run
else
    exit 0
fi

sleep 3

#Some variables that make this script use test
#These can be sourced and the same sript used for both ENV

#Published as logs at http://esb01.esss.lu.se
LOGPATH="/var/www/html/pagerotest.log"

#Incoming folder from pagero
MYPATH="/sftp/pagerotest/home/from_pagero/"

#Path to publish to for integration with agresso
REMOTEPATH="/mnt/erpshare/agrtest/Svefakt/In/Efakturor/"

#Here we find all new xml files in the drop-zone specified above
DAFILES=$(/bin/find "$MYPATH" -name '*.xml' -type f | /bin/uniq | /bin/sort ) #| /usr/bin/tr '[:upper:]' '[:lower:]'

#Function to move and edit files on the fly
function movefiles {
for xmlfiles in $DAFILES; do

    #Here we get the number from any xml file
    DANUM="$(/bin/echo "$xmlfiles" | /usr/bin/rev | /usr/bin/cut -d \. -f2 | /usr/bin/cut -d \_ -f1 | /usr/bin/rev)"

    #Making the working folder in tmp
    /bin/mkdir -p /tmp/"$DANUM"/invoice_"$DANUM"

    #Moving the xml file to the temporary folder
    /bin/mv --force $xmlfiles /tmp/"$DANUM"/

    #Locating any attachments that contain the same number as above
    for attachements in $(/bin/find "$MYPATH" -type f | /bin/grep "$DANUM" | /bin/uniq | /bin/sort ); do

        #Some extra fidling to get the name of the attachment
        ONEFILE=$(/bin/basename $attachements)
        DAFILE=$(echo $ONEFILE | /usr/bin/tr -d '\n')

        #Editing the xml file using the found attachement name from above
        /bin/sed -i "s/$DAFILE/urn\:sfti\:documents\:object\:$DAFILE/g" /tmp/"$DANUM"/*.xml

        #Moving the same attachment to the temporary folder
        /bin/mv --force $attachements /tmp/"$DANUM"/invoice_"$DANUM"

    done
    #Moving the temporary folder to the remote path
    /bin/mv --force /tmp/"$DANUM"/* "$REMOTEPATH"

    #Logging to /var/log/messages
    /bin/logger "$DANUM moved to fileserver"

    #Logging to the published file.
    /bin/echo $(date +%Y-%m-%d:%H:%M:%S) $DANUM moved to fileserver >>$LOGPATH

    #Deleting any leftover temporary folders
    /bin/rm -rf /tmp/"$DANUM"/
done
}

#Function to make sure that the fileserver is unmounted, there can actually be more than one mount
#registed at the same path and the below snurra makes sure that the server is unmounted
function unmountfileserver {
while (( $(/bin/mount | /bin/grep fileserver01 | /bin/wc -l) >=1 ));do
    umount /mnt/erpshare/
done
}

#Start of actual script
unmountfileserver

#Remove old kerberos ticket for the host
/bin/kdestroy -A

#Get new kerberos ticket to use for auth at fileserver
/bin/kinit $(/bin/hostname -s | /usr/bin/tr '[:lower:]' '[:upper:]')$ -k -t /etc/krb5.keytab

#Prepare for the mount
PRINCIPAL=$(/bin/klist | /bin/grep "Default principal" | /bin/cut -d \: -f2 | /bin/tr -d ' ')
#The actual mount
/bin/mount -t cifs -o user="$PRINCIPAL",sec=krb5 //fileserver01.esss.lu.se/ERPShare /mnt/erpshare

#Check if the mount was successfull
DAMOUNT="$(/bin/echo $?)"
if [[ ! "$DAMOUNT" = 0 ]]; then
    #Not mounted so now its time to die
    unmountfileserver
    #Clean up of script
    /bin/rm -rf /tmp/mountedfileserver.run
    exit 1
fi

if [[ ! $DAFILES ]]; then
    #No files found at incoming path
    unmountfileserver
    #Clean up of script
    /bin/rm -rf /tmp/mountedfileserver.run
    exit 1
else
    #Some files found at incoming path, now time to process
    movefiles
    unmountfileserver
    #Clean up of script
    /bin/rm -rf /tmp/mountedfileserver.run
fi



exit 0

