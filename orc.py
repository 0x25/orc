#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
author: Ox25
date: 09/08/2023
description: run parallel tasks by block with multithreads

/////// //////// ///////
//   // //   //  //   //
//   // //////        //
//   // //   //  //   //
/////// //   /// /////// V1.1
"""

from yaml.loader import SafeLoader
import os.path
import sys, argparse, yaml, re
from multiprocessing import Pool
import shlex, subprocess


def load_yaml_config(file):
  """Load YAML file configuration and returns a Python object"""

  if os.path.isfile(file):
    with open(file) as f:
      data = yaml.load(f, Loader=SafeLoader)
      return data
  else:
    sys.exit('ERROR : no file/wrong path')


def replace_clis(str_list,datas):
  """ Generate all possible cmd with a command string and the dict of item to replace """

  if not isinstance(str_list,list) : str_list = [str_list]
  for data in datas:
    key = list(data.keys())[0]
    values = data[key]

    if isinstance(values,list):
      # list
      str_tmp = []
      for k,str in enumerate(str_list):
        if str.find('{{' + key + '}}') != -1:
          for value in values:
            item = {}
            item[key] = value
            str_tmp = str_tmp + replace_clis([str],[item])
          str_list = str_tmp
    else:
      # str
      for k,str in enumerate(str_list):
        if str.find('{{' + key + '}}') != -1:
          str_list[k] = str.replace('{{'+key+'}}',values)

  return str_list


def format_clis(vars,block):
  """ format all command and return a list"""

  clis = block['clis']
  clis_formated = []
  outs_formated = []
  for cli in clis:
    if isinstance(cli,dict):
      clis_formated = clis_formated + replace_clis(cli['cli'],vars)
      #print(clis_formated)
      outs_formated = outs_formated + replace_clis(cli['out'],vars)
      #print(outs_formated)
    else:
      clis_tmp = replace_clis(cli,vars)
      clis_formated = clis_formated + clis_tmp
      #print(f" out {clis_formated}")
      outs_formated = outs_formated + [False]*len(clis_tmp)
      #print(outs_formated)

  return {'clis':clis_formated, 'out':outs_formated}

def blockCmd(job):
  ''' Task to run the cli'''
  pid = os.getpid()
  cli = job['cli']
  log = job['log']
  print(f"   [{pid}] Task cli [{cli}] log [{log}]")

  args = shlex.split(cli)
  if log is not False:
    print(f"    \033[0;32m[{pid}] Log outpput to file: [{log}]\033[0m")
    p = subprocess.Popen(args,stdout=open(log,'a'))
  else:
    #p = subprocess.Popen(args,stdout=subprocess.PIPE)
    p = subprocess.Popen(args,stdout=open('/dev/null', 'w'))
  
  p.wait()

def files_to_vars(files):
  ''' extract vars from files'''
  tmpdct = []
  for item in files:
    var = list(item.keys())[0]
    file = item[var]
    tmplst = {}
    if os.path.isfile(file):
      with open(file,'r') as f:
        tmplst[var] = f.read().splitlines()
        tmpdct.append(tmplst)
    else:
      sys.exit('ERROR : no file/wrong path for files ' + file)

  return tmpdct

def main():
  """ main code """

  default_thread = 4
  default_config_name = 'orc.yaml'

  description = "\033[1;32m Run tasks by blocks with multitreads \033[0m"
  epilog = "\033[0;35m $$ XMR 4Ahnr36hZQsJ3P6jowXvs7cLkSVbkq2KyfQBVURYVftcj9tDoA592wT1jskroZEk2QDEZFPYMLqVvJWZHecFwQ9nL15SzRG\033[0m"

  if len(sys.argv) <= 1:
    print(f"\033[1;32mStart ORC with default parameters : yaml file [{default_config_name}] and thread [{default_thread}]. Use -h to show help.\033[0m\n")

  parser = argparse.ArgumentParser(description=description, epilog=epilog)
  parser.add_argument('-t','--thread', type=int, default=default_thread, help='Number of default concurent thread in block if not set [4]')
  parser.add_argument('-c','--conf', default=default_config_name, help='YAML config file, default name is [orc.yaml]')
  args = parser.parse_args()

  default_thread = args.thread
  yaml_file = args.conf
  
  print(f"\033[0;33m-Load yaml file [{yaml_file}]\033[0m")
  config_datas = load_yaml_config(yaml_file)

  variables = config_datas['vars']
  files = config_datas['files']
  blocks = config_datas['blocks']

  variables += files_to_vars(files)

  _final = {}
  for elem in variables:
    for key, value in elem.items():
      _final[key] = [] if key not in _final.keys() else list(_final[key])
      if isinstance(value, list):
        for item in value:
          _final.setdefault(key, []).append(item)
      else:
        _final.setdefault(key, []).append(value)
      _final[key] = list(set(_final[key]))
  
  all_variables = []
  for key,value in _final.items():
    t = {}
    if len(value) > 1:
      t[key] = value
    else:
      t[key] = value[0]
    all_variables.append(t)

  for block in blocks:
    block_name = block['block']
    if block['threads']:
      block_threads = block['threads']
    else:
      block_threads = default_thread
    
    print(f"\033[0;34m--Block [{block_name}]\033[0m")
    clis = format_clis(all_variables,block)
    #print(clis)
    jobs = []

    for key,cli in enumerate(clis['clis']):
      jobs.append({'cli':cli,'log':clis['out'][key]})

    p = Pool(block_threads)
    p.map(blockCmd,jobs)
    p.close()
    p.join()

# main
if __name__ == '__main__':
        main()
