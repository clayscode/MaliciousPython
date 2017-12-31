from flask import Flask
from flask import jsonify

app = Flask(__name__)


commands = [
        { 'id':'0',
          'command':u'http-dos 127.0.0.1:80',
          'end_cond':u'inf',
        }
        ]

@app.route('/commands', methods=['GET'])
def get_commands():
    return jsonify({'commands': commands})

app.run(host='127.0.0.1')



