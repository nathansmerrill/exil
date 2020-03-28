#!/usr/bin/python3 -u
from flask import Flask, send_file, request
from flask_socketio import SocketIO, emit
from datetime import datetime

from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
sio = SocketIO(app, cors_allowed_origins='*')

PORT = 4000

@app.route('/')
@app.route('/<path:path>')
def get(path='index.html'):
    return send_file(f'../public/{path}')

@sio.on('connect')
def connect():
    sprint('connect', f'{request.sid} {request.remote_addr}')

@sio.on('disconnect')
def disconnect():
    sprint('disconnect', f'{request.sid} {request.remote_addr}')

def sprint(tag, text, timestamp=True):
    out = f'[{tag.upper()}'
    if timestamp:
        out += f' {datetime.now().strftime("%d-%b-%Y %-I:%M:%S %p")}'
    out += f'] {text}'
    print(out)

if __name__ == '__main__':
    sprint('server', 'Initializing...')
    players = {}
    sprint('server', f'Starting web server on port {PORT}')
    sio.run(app, host='0.0.0.0', port=PORT)
