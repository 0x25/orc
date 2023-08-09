#!/bin/bash
# Merge multiple files sort and deduplicate
# 2022

if [ $# -lt 3 ]; then
  echo "Help"
  echo "merge.sh file1 file2 [...fileN] outfile"
  exit 1
fi

args=( $@ )
outfile=${args[-1]}

unset args[-1]

cat ${args[@]} | sort -u | uniq > $outfile
