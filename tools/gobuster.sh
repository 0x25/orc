#!/bin/bash
# exemple of script bash to bruteforce dns and export dnsname to a file

/opt/gobuster/gobuster dns -d $1 -w /opt/gobuster/subdomains-top1million-5000.txt -r 1.1.1.1 -q | awk -F " " '{print $2}' > $2

