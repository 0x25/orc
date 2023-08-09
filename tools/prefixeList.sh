#!/bin/bash
# add $1:// on all $2 file line and output in $3
# usefull for prefix http and https to list of sub domain
# maybe httpx tool is a good alternative ^^

sed -e "s#^#$1://#" $2 > $3
