#!/bin/bash

DAPATH='/sftp/sebkort/home'
#DAPATH='/tmp/sebkort'

if ! [ -f /tmp/sebkort.run ]; then
    touch /tmp/sebkort.run
else
    exit 0
fi

sleep 30

/bin/find $DAPATH -name '*.*' -exec sh -c 'a=$(/bin/echo "$0" | /usr/bin/sed -r "s/([^.]*)\$/\L\1/");[ "$a" != "$0" ] && /usr/bin/mv "$0" "$a" ' {} \;
THEFILE=$(/bin/find  $DAPATH -name '*.pdf' -type f)
for f in $THEFILE; do
    echo $f
    /bin/echo "See attached file" | /bin/mailx -vv -r "noreply@esss.se"
                                               -s "Your sebcard file"
                                               -S smtp=mail.esss.lu.se:25
                                               -S smtp-use-starttls
                                               -S smtp-auth=login
                                               -S smtp-auth-user="kalle"
                                               -S smtp-auth-password="kalle"
                                               -S ssl-verify=ignore
                                               -S nss-config-dir=/etc/pki/nssdb/
                                               -a $f
                                               invoices@esss.se
    #/bin/rm -rf $THEFILE
    /usr/bin/mv $f /home/sebkort/
    /bin/logger "sent $f to invoices"
    /bin/echo $(date +%Y-%m-%d:%H:%M:%S) sent $f to invoices >>/var/log/sebcard.log
    sleep 30
done
#echo "See attatced file" | mailx -r "noreply@esss.se" -s "Your sebcard file" -a $THEFILE invoices@esss.se
/bin/rm -rf /tmp/sebkort.run
exit 0

