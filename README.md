
![ORC](https://github.com/0x25/orc/blob/main/orc.png?raw=true)

# Orc
Orc is a tool write in python3 to run command line by block.
The script read a [yaml](https://en.wikipedia.org/wiki/YAML) file to retreive variables and commands. The code run multiple commands simultaneously block after block.

**Stop writing the same commands day after day, just edit variables and run the script.** 

## Help
    usage: orc.py [-h] [-t THREAD] [-c CONF]

     Run tasks by blocks with multitreads 

    optional arguments:
      -h, --help                  Show this help message and exit
      -t THREAD, --thread THREAD  Number of default concurent thread in block if not set
      -c CONF, --conf CONF        YAML config file, default name is [orc.yaml]

## Variables
A templating mecanisme is used to replace variables in commands. A variable can be a simple value or a list of value.

<u>Example of variables configuration:</u>

    vars:
      - myvalue: somedata
      - mylist:
        - data1
        - data2

## Template
Each name of variable can be use in commands.
For example '**myvalue**' can be used with the **{{myvalue}}** representation in the command.

## Blocks
Blocks is a list of block.
Each block contain a *block* name, and *clis* (command to run) and optionally *threads* (number of threads to use to run this block).

clis is a list a command. each command can be write in 2 ways:

    clis:
      - 'my command 1 {{myvalue}}'
      - ...
    
Run the command only

    clis:
      - cli: 'my command 1'
        out: 'name of logfile'
      - ...
    
Run the command and save the stdout to the out file.
You can mix both type in clis.

## yaml example

<u>Example of block configuration:</u>
  ```
---
#
# YAML Config example
#

vars:
  - ip: 192.168.1.10
  - website: www.website.ltd
  - domains: 
    - domain1.ltd
    - domain2.ltd
  - ips:
    - 10.0.0.1
    - 10.0.0.2
  - folder: result
  - protocols:
    - http
    - https

blocks:
  - block: 'create folders structure'
    threads: 1
    clis:
      - 'mkdir -p {{folder}}/nmap'
      - 'mkdir -p {{folder}}/nikto'
      - 'mkdir -p {{folder}}/whois'
      - 'mkdir -p {{folder}}/dns'

  - block: 'Discover target'
    threads: 4
    clis: 
      - cli: 'nslookup {{website}}'
        out: '{{folder}}/dns/nslookup_{{website}}.log'
      - cli : 'dig any +noall +answer {{website}} @8.8.8.8'
        out: '{{folder}}/dns/dig_{{website}}.log'
      - cli: 'host {{domains}}'
        out: '{{folder}}/dns/host_{{domains}}.log'
      - cli: 'whois {{domains}}'
        out: '{{folder}}/whois/whois_{{domains}}.log'

  - block: 'Fast nmap discover (top 100)'
    threads: 4
    clis: 
      - 'nmap -v0 --open -Pn -n -F -sC -sV -T5 -oA {{folder}}/nmap/fast_{{ips}} {{ips}}'

  - block: 'Normal nmap discover (top 1000) and nikto'
    threads: 4
    clis: 
      - 'nmap -v0 --open -Pn -n -sC -sV -T5 -oA {{folder}}/nmap/normal_{{ips}} {{ips}}'
      #- 'nikto -maxtime 20m -nointeractive -host {{protocols}}://{{website}} -output {{folder}}/nikto/{{protocols}}_{{website}}.log -Format txt'
      - 'python3 tools/nmaptocsv.py -x result/nmap/fast_{{ips}}.xml -o result/nmap/fast_{{ips}}.csv'

#  - block: 'name'
#    cli:
#      - ''
```    
    
## To do

 - Add some yaml file for generic actions
 - Add tools in tools folder 
 - Patch 
 - Add your pull request \o/
 - ...
