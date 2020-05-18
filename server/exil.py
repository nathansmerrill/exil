#!/usr/bin/python3 -u

import math
from datetime import datetime
from threading import RLock

import noise
from config import DevelopmentConfig
from flask import Flask, send_file, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
sio = SocketIO(app, cors_allowed_origins='*')

PORT = 4000

PLAYER_SPEED = 0.1
PLAYER_STRAFE_MODIFIER = 0.7
RENDER_DISTANCE = 8

class Player:
    def __init__(self, sid, x, y, z):
        self.sid = sid
        self.x = x
        self.y = y
        self.z = z
        self.inputs = {
            'keyboard': [],
            'actions': [],
            'pitch': 0,
            'yaw': 0
        }

    def getDict(self):
        return self.__dict__

class Chunk:
    def __init__(self, x, z): # X and Z are CHUNK COORDINATES, not 3D COORDINATES
        self.x = x
        self.z = z
        self.data = {}
        self.obj = {} # <-- to be used for models LATER!
        for xh in range(0, 50):
            for yh in range(0, 50):
                self.data[xh * 50 + yh] = getHeightMapAtPoint(x * 50 + xh, z * 50 + yh)

    def getDict(self):
        return self.__dict__


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

@sio.on('inputs')
def receiveInputs(inputs):
    players[request.sid].inputs = inputs

def sprint(tag, text, timestamp=True):
    out = f'[{tag.upper()}'
    if timestamp:
        out += f' {datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")}'
    out += f'] {text}'
    print(out)

def runGameLoop():
    while True:
        sio.sleep(0.01)
        playersLock.acquire()
        for sid in players: # 1: SEND PLAYER DATA OUT
            player = players[sid]
            if 'w' in player.inputs['keyboard']:
                player.x += math.sin(player.inputs['yaw'] + math.pi) * PLAYER_SPEED
                player.z += math.cos(player.inputs['yaw'] + math.pi) * PLAYER_SPEED
            elif 's' in player.inputs['keyboard']:
                player.x += math.sin(player.inputs['yaw']) * PLAYER_SPEED * PLAYER_STRAFE_MODIFIER
                player.z += math.cos(player.inputs['yaw']) * PLAYER_SPEED * PLAYER_STRAFE_MODIFIER
            if 'd' in player.inputs['keyboard']:
                player.x += math.sin(player.inputs['yaw'] + math.pi / 2) * PLAYER_SPEED * PLAYER_STRAFE_MODIFIER
                player.z += math.cos(player.inputs['yaw'] + math.pi / 2) * PLAYER_SPEED * PLAYER_STRAFE_MODIFIER
            elif 'a' in player.inputs['keyboard']:
                player.x += math.sin(player.inputs['yaw'] - math.pi / 2) * PLAYER_SPEED * PLAYER_STRAFE_MODIFIER
                player.z += math.cos(player.inputs['yaw'] - math.pi / 2) * PLAYER_SPEED * PLAYER_STRAFE_MODIFIER
            player.y = getHeightMapAtPoint(player.x, player.y) + 1.8
        sendPlayerDict = {}
        for sid in players:
            sendPlayerDict[sid] = players[sid].getDict()
        sio.emit('players', sendPlayerDict, broadcast=True)
        for sid in players:
            sio.emit('chunks', Chunk(0, 0).getDict(), broadcast=True)
        playersLock.release()

noiseOctaves = [

    {
        'freq': 0.005,
        'amp': 100,
        'zDepth': 100,
    }
]

def getHeightMapAtPoint(x, y):
    h = 0
    for octave in noiseOctaves:
        h += (noise.snoise3(x * octave['freq'], y * octave['freq'], octave['zDepth']) * octave['amp'])
    return h

if __name__ == '__main__':
    sprint('server', 'Initializing...')
    sprint('server', 'Initializing variables...')
    players = {}
    playersLock = RLock()

    sprint('server', 'Initializing game loop...')
    gameLoopThread = sio.start_background_task(target=runGameLoop)

    sprint('server', f'Starting web server on port {PORT}')
    sio.run(app, host='0.0.0.0', port=PORT)
