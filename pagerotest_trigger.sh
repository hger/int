#!/bin/bash

tail -1  /var/log/secure | grep "session closed for user pagerotest"
FOUNDIT=$(echo $?)
if [[ ! $FOUNDIT = 0 ]];then
    echo nothing
else
    echo do stuff now
    /usr/local/bin/pagerotest.sh
fi

