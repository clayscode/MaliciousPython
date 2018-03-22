from flask import Flask
from flask import jsonify
from flask import send_from_directory
import os
import json
import subprocess

app = Flask(__name__)

previous_mod = os.path.getmtime('commands.json')

with open('commands.json') as command_data:
    commands = json.load(command_data)

@app.route('/commands', methods=['GET'])
def get_commands():

    #if previous_mod != os.path.getmtime('commands.json'):
    #    with open('commands.json') as command_data:
    #        commands = json.load(command_data)

    return jsonify({'commands': commands})

@app.route('/files/<path:filename>', methods=['GET'])
def send_files(filename):
   return send_from_directory(directory='files', filename=filename) 

@app.route('/connect/<port>', methods=['GET'])
def open_port(port):
    print port
    subprocess.Popen('screen -dm bash -c "nc -vl 0.0.0.0 -p {}"'.format(port), shell=True)    
    return 'done'

if __name__ == "__main__":
    app.run(threaded=True,host='0.0.0.0')



