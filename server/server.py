from flask import Flask, send_file, request
from flask_socketio import SocketIO, emit

from datetime import datetime

app = Flask(__name__)
sio = SocketIO(app)

def sprint(tag, message, timestamp=True):
    out = '['
    out += tag
    if timestamp:
        out += ' '
        out += datetime.now().strftime("%d-%b-%Y %-I:%M:%S %p")
    out += '] '
    out += message
    print(out)

@app.route('/')
@app.route('/<path:path>')
def index(path = 'index.html'):
    return send_file(f'../public/{path}')

@sio.on('connect')
def connect():
    sprint('CONNECT', request.sid)

@sio.on('disconnect')
def disconnect():
    sprint('DISCONNECT', request.sid)

if __name__ == '__main__':
    sio.run(app, port=4000)
    # app.run(port=4000)
