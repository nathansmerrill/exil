#!/usr/bin/python3 -u
import eventlet
eventlet.monkey_patch()

from flask import Flask, send_file, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
sio = SocketIO(app)

@app.route('/')
@app.route('/<path:path>')
def index(path = 'index.html'):
    return send_file(f'../public/{path}')

if __name__ == '__main__':
    app.run(port=4000)
