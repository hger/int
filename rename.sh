#!/bin/bash

fixit (){
mkdir -p /tmp/sebkort/
touch /tmp/sebkort/Hej.Pdf
touch /tmp/sebkort/hoj.pdf
touch /tmp/sebkort/BALLE.PDF
}

#fixit

#for f in /tmp/sebkort/*; do
#    mv "$f" "$f.tmp"
#    mv "$f" "`basename "$f" .html`.txt"
#    mv "$f.tmp" $(echo $f | tr "[:upper:]" "[:lower:]")
#done
find /tmp/sebkort/ -name '*.*' -exec sh -c 'a=$(echo "$0" | sed -r "s/([^.]*)\$/\L\1/");[ "$a" != "$0" ] && mv "$0" "$a" ' {} \;
