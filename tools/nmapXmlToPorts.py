#!/usr/bin/env python3
# 0x25
# 19/05/2022

from bs4 import BeautifulSoup
import json
import sys

if len(sys.argv) != 3:
  print("Wrong number of parameters")
  print("nmap.xml outfile.txt")
  sys.exit()

xml_parser = BeautifulSoup(open(sys.argv[1]), 'xml')
f = open(sys.argv[2], 'a')

for host in xml_parser.find_all('host'):
  hostname = host.hostname["name"]

  for port in host.find_all('port'):
    portid = port["portid"]
    protocol = port["protocol"]
    name = port.service["name"]
    out = "{} {}://{}:{}\n".format(protocol,name,hostname,portid)
    f.write(out)

f.close()
