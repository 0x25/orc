#!/usr/bin/env python3

__author__      = "0x25"
__copyright__   = "GNU General Public Licence"
__date__        = "06/07/2023"

import json
import time
import requests
import argparse
import sys

default_sleep = 20
default_output = ''
default_limit = 100

description='extract sub domain from VirusTotal - The Public API is limited to 500 requests per day and a rate of 4 requests per minute.'
epilog=''

parser = argparse.ArgumentParser(description=description, epilog=epilog)
parser.add_argument('-o','--output',default=default_output,required=False, help='save output to file')
parser.add_argument('-s','--sleep',default=default_sleep,required=False, help='add delay in process')
parser.add_argument('-l','--limit',default=default_limit,required=False, help='number of result')
parser.add_argument('-d','--domain',required=True, help='domain to get subdomain')
parser.add_argument('-k','--key',required=True, help='api key')
args = parser.parse_args()

api = args.key
domain = args.domain
output = args.output
sleep = int(args.sleep)
limit = args.limit

if output != '':
    f = open(output, 'w')

url = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains?limit={limit}"

time.sleep(sleep)

headers = {'X-Apikey': api}
result = requests.get(url, headers=headers)

if result.status_code != 200:
    print("Error HTTP code response : {}".format(result.status_code))
    sys.exit(1)

datas = result.json()

for data in datas['data']:
    sub_domain = data['id']
    if output != '' :
        f.write("{}\n".format(sub_domain))
    print(sub_domain)

if output != '':
    f.close()
