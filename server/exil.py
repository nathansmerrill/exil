#!/usr/bin/python3 -u
from flask import Flask, send_file, request
from flask_socketio import SocketIO, emit
from threading import Thread, RLock
from datetime import datetime

from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
sio = SocketIO(app, cors_allowed_origins='*')

PORT = 4000

class Player:
    def __init__(self, sid, x, y, z):
        self.sid = sid
        self.x = x
        self.y = y
        self.z = z
        self.inputs = {
            'keyboard': [],
            'mouseX': 0,
            'mouseY': 0
        }

@app.route('/')
@app.route('/<path:path>')
def get(path='index.html'):
    return send_file(f'../public/{path}')

@sio.on('connect')
def connect():
    sprint('connect', f'{request.sid} {request.remote_addr}')
    playersLock.acquire()
    players[request.sid] = Player(request.sid, 0, 0, 0)
    playersLock.release()

@sio.on('disconnect')
def disconnect():
    sprint('disconnect', f'{request.sid} {request.remote_addr}')
    playersLock.acquire()
    players.pop(request.sid)
    playersLock.release()

def sprint(tag, text, timestamp=True):
    out = f'[{tag.upper()}'
    if timestamp:
        out += f' {datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")}'
    out += f'] {text}'
    print(out)

def runGameLoop():
    while True:
        playersLock.acquire()
        for sid in players:
            # print(f'Running game loop on {sid}')
            pass
        playersLock.release()

if __name__ == '__main__':
    sprint('server', 'Initializing...')
    sprint('server', 'Initializing variables...')
    players = {}
    playersLock = RLock()

    sprint('server', 'Initializing game loop...')
    gameLoopThread = Thread(target=runGameLoop)
    gameLoopThread.start()

    sprint('server', f'Starting web server on port {PORT}')
    sio.run(app, host='0.0.0.0', port=PORT)
