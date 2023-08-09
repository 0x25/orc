#!/bin/bash
#test line by line ($1 file) if a DNS resolution exist and output dom in $2

while read -r line; do

  host $line &>/dev/null
  if [ $? -eq 0 ]; then
    echo $line >> $2
  fi
done < $1
