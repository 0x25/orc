#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
author: Ox25
date: 29/09/2023
update: 29/10/2025
description: run parallel tasks by block with multithreads and variables auto completion with low CPU/memory usage ;)

/////// //////// ///////
//   // //   //  //   //
//   // //////        //
//   // //   //  //   //
/////// //   /// /////// V2.1


EXAMPLE of config.yaml

files:
  - file: liste.txt

vars:
  - folder: Result:datePrefix
  - test: toto
  - protocols:
    - HTtp
    - https
    - test/12

blocks:
  - block: 'create folders structure'
    threads: 1
    clis:
      - 'mkdir -p {{folder:lower}}/nmap'
      - 'mkdir -p {{folder:lower}}/{{protocols:lower:replace(/,_)}}'

blocks:
  - block: 'second block'
  ...

"""

from yaml.loader import SafeLoader
import os.path
import sys, argparse, yaml, re
from multiprocessing import Pool
import shlex, subprocess
import re
import random
import string
import datetime


def load_yaml_config(file):
  """
    Load YAML file configuration and returns a Python object
  """

  if os.path.isfile(file):
    with open(file) as f:
      data = yaml.load(f, Loader=SafeLoader)
      return data
  else:
    sys.exit('ERROR : no file/wrong path')

def is_match(key,cli,values):
  """
    Search if key have function like myVar:upper:randPrefix(8,_) or juste myVar
  """
  out = {'key':'','handle':'','values':''}
  if cli.find('{{' + key + '}}') != -1:
    out['key'] = key
    out['handle'] = ''
    out['values'] = values

  else:
    pattern = r"{{(" + key + "):(.*?)}}"
    res = re.search(pattern,cli)
    if res:
      out['key'] = res.group(1)
      out['handle'] = res.group(2)
      out['values'] = handle_match(res.group(2),values)

  return out

def handle_match(handle,values):
  """
    run all functions concatenate to a var. Multiple function can be set lower:randSuffix(4)
    function:
      replace(a,b)
      upper
      lower
      prefix(value)
      suffix(value)
      randSuffix(len)
      randSuffix(len,sep)
      randPrefix(len)
      randPrefix(len,sep)
      dateSuffix
      datePrefix
  """
  
  handles = handle.split(':')
  pattern = r"(\w+)(\(([^)]*)\)){0,1}" # function
  if isinstance(values,list):
    return values
  else:
    tvalue = values
    for function in handles:
      functionInfo = re.search(pattern,function)
      
      functionName = functionInfo.group(1)
      functionArgs = functionInfo.group(3)
      if functionArgs is None:
        functionArgs = ''
      else:
        functionArgs = functionArgs.split(',')
      
      # place to declare function in filter 
      # replace(a,b)
      if functionName == 'replace' and len(functionArgs) == 2 :
        
        tvalue = tvalue.replace(functionArgs[0],functionArgs[1])
      
      # upper
      elif functionName == 'upper':
        tvalue = tvalue.upper()
      
      # lower
      elif functionName == 'lower':
        tvalue = tvalue.lower()
      
      # prefix(value)
      elif functionName == 'prefix' and len(functionArgs) == 1:
        tvalue = functionArgs[0] + tvalue
      
      #suffix(value)
      elif functionName == 'suffix' and len(functionArgs) == 1:
        tvalue = tvalue + functionArgs[0]
        
      #randSuffix(len)
      elif functionName == 'randSuffix' and len(functionArgs) == 1:
        length = int(functionArgs[0])
        tvalue = ''.join(random.choices(string.ascii_letters + string.digits, k=length)) + tvalue

      #randSuffix(len,sep)
      elif functionName == 'randSuffix' and len(functionArgs) == 2:
        length = int(functionArgs[0] )
        tvalue = ''.join(random.choices(string.ascii_letters + string.digits, k=length)) + functionArgs[1] + tvalue

      #randPrefix(len)
      elif functionName == 'randPrefix' and len(functionArgs) == 1:
        length = int(functionArgs[0])
        tvalue = tvalue + ''.join(random.choices(string.ascii_letters + string.digits, k=length))

      #randPrefix(len,sep)
      elif functionName == 'randPrefix' and len(functionArgs) == 2:
        length = int(functionArgs[0])
        tvalue = tvalue + functionArgs[1] + ''.join(random.choices(string.ascii_letters + string.digits, k=length))
      
      # dateSuffix
      elif functionName == 'dateSuffix':
        now = datetime.datetime.now()
        format_string = "%Y_%m_%d_%Hh%Mm%S"
        dateName = now.strftime(format_string)
        tvalue = dateName + "_" + tvalue
        
      # datePrefix
      elif functionName == 'datePrefix':
        now = datetime.datetime.now()
        format_string = "%Y_%m_%d_%Hh%Mm%S"
        dateName = now.strftime(format_string)
        tvalue = tvalue + "_" + dateName
        
      else:
        tvalue = tvalue
          
      tvalues = tvalue
      
    return tvalues


def replace_clis(str_list,datas):
  """
    Generate all possible cmd recursively
  """
  if not isinstance(str_list,list) : str_list = [str_list]
  for data in datas:
    key = list(data.keys())[0]
    values = data[key]

    if isinstance(values,list):
      # list
      str_tmp = []
      for k,str in enumerate(str_list):
        res = is_match(key,str,values)
        
        if 'values' in res and res['values'] != '':
          for value in res['values']:
            item = {}
            item[res['key']] = value
            str_tmp = str_tmp + replace_clis([str],[item])
          str_list = str_tmp
    else:
      # str
      for k,str in enumerate(str_list):
        res = is_match(key,str,values)
        
        tkey = res['key']
        if 'handle' in res and res['handle'] != '':
           tkey = tkey + ':' +res['handle']
        if res is not None:
          str_list[k] = str.replace('{{'+ tkey +'}}',res['values'])

  return str_list


def format_clis(vars,block):
  """
    Format all command and return a list
  """
  
  clis = block['clis']
  clis_formated = []
  outs_formated = []
  for cli in clis:
    if isinstance(cli,dict):
      cmd = cli['cli']
      out = cli['out']
      clis_len = 0
      clis_tmp = replace_clis(cmd,vars)
      replace = True
      while replace :
        clis_tmp = replace_clis(clis_tmp,vars)
        tmp_len = len(clis_tmp)

        if clis_len == tmp_len:
          replace = False
        clis_len = tmp_len

      out_len = 0
      out_tmp = replace_clis(out,vars)
      replace = True
      while replace :
        out_tmp = replace_clis(out_tmp,vars)
        tmp_len = len(out_tmp)

        if out_len == tmp_len:
          replace = False
        out_len = tmp_len

      clis_formated = clis_formated + clis_tmp
      outs_formated = outs_formated + out_tmp
    else:
      clis_len = 0
      clis_tmp = replace_clis(cli,vars)
      replace = True
      while replace :
        clis_tmp = replace_clis(clis_tmp,vars)
        tmp_len = len(clis_tmp)

        if clis_len == tmp_len:
          replace = False
        clis_len = tmp_len

      clis_formated = clis_formated + clis_tmp
      outs_formated = outs_formated + [False]*len(clis_tmp)

  return {'clis':clis_formated, 'out':outs_formated}

def blockCmd(job):
  """ 
    Task (block) to run the cli
  """
  
  pid = os.getpid()
  cli = job['cli']
  log = job['log']
  
  print(f"   [{pid}] Task cli [{cli}] log [{log}]")

  args = shlex.split(cli)
  if log is not False:
    print(f"    \033[0;32m[{pid}] Log outpput to file: [{log}]\033[0m")
    p = subprocess.Popen(args,stdout=open(log,'a'))
  else:
    p = subprocess.Popen(args,stdout=open('/dev/null', 'w'))
  
  p.wait()

def files_to_vars(files):
  """
    Extract vars from files to merge with vars
  """
  
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
  default_enable = 'True'
  
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

  if 'vars' in config_datas:
    variables = config_datas['vars']
  else:
    variables = []

  if 'files' in config_datas:
    files = config_datas['files']
  else:
    files = []
    
  if 'blocks' not in config_datas:
    sys.exit("Error: Need blocks")
  else:
    blocks = config_datas['blocks']

  if files is not None:
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
      datas = value[0].split(":",1)
      if len(datas) > 1:
        res = handle_match(value[0],datas[0])
        t[key] = [res]
      else:
        t[key] = value
    all_variables.append(t)
  
  for block in blocks:
    block_name = block['block']

    if 'enable' in block:
      block_enable = block['enable']
    else:
      block_enable = default_enable

    if 'threads' in block:
      block_threads = block['threads']
    else:
      block_threads = default_thread
    
    print(f"\033[0;34m--Block [{block_name}]\033[0m")
    if block_enable != 'True':
      print(f"    \033[0;31mblock disable\033[0m")
      continue # back to for loop

    clis = format_clis(all_variables,block)

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
