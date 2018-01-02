from flask import Flask
from flask import jsonify

app = Flask(__name__)


commands = [
        { 'id':'0',
          'command':u'send-shell',
          'target':u'127.0.0.1:8008',
          'end_cond':u'inf',
          'kill-now':u'False',
        }
        ]

@app.route('/commands', methods=['GET'])
def get_commands():
    return jsonify({'commands': commands})

app.run(host='127.0.0.1')



