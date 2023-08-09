#!/usr/bin/env python3


import argparse
import requests
import os.path
import sys
import urllib3
from urllib.parse import urlparse


urllib3.disable_warnings()

def main():

  description = "Check URL redirection, deduplicate and format a new list."
  headers = headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'}

  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('-f','--file', help='file with URL line by line', required=True)
  parser.add_argument('-o','--out', help='output file')
  parser.add_argument('-d','--debug',default=0, help='active debug -d 1')
  args = parser.parse_args()

  file = args.file
  out = args.out
  if args.debug != '':
    debug = 1

  if os.path.isfile(file) == False:
    print("ERROR: file don't exist\n")
    sys.exit(1)

  file_handler = open(file, 'r')
  lines = file_handler.readlines()
  file_handler.close()

  urls = []
  for line in lines:
    url_file = line.strip()
    try:
      response = requests.head(url_file, headers=headers, verify=False, allow_redirects=True, timeout=4)
    except:
      print("ERROR: connexion fail [{}]".format(url_file))
      response_url = ''
      pass

    response_url = response.url

    url = urlparse(response.url)
    url_last = url.scheme + "://" + url.hostname
    if debug == 1:
      print("DEBUG: {}".format(url_last))

    if url_last not in urls and response_url != '':
      urls.append(url_last)

  if out is not None:
    with open(out, 'a') as out_file:
      for url in urls:
        out_file.write("{}\n".format(url))
  else:
   for url in urls:
    print(url)


# main
if __name__ == '__main__':
        main()
