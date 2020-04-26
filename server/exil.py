#!/usr/bin/python3 -u
import time

from flask import Flask, send_file, request
from flask_socketio import SocketIO, emit
from threading import Thread, RLock, Lock
from datetime import datetime
from config import DevelopmentConfig
import json, math

asyncMode = None

app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
sio = SocketIO(app, async_mode=asyncMode, cors_allowed_origins='*')

PORT = 4000

gamerules = {
    'PLAYER_SPEED': 0.1,
    'PLAYER_STRAFE_MODIFIER': 0.7
}

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
    print(inputs['keyboard'], '  ', players[request.sid].getDict())


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
        for sid in players:
            player = players[sid]
            if 'w' in player.inputs['keyboard']:
                player.x += math.sin(player.inputs['yaw'] + math.pi) * gamerules['PLAYER_SPEED']
                player.z += math.cos(player.inputs['yaw'] + math.pi) * gamerules['PLAYER_SPEED']
            elif 's' in player.inputs['keyboard']:
                player.x += math.sin(player.inputs['yaw']) * gamerules['PLAYER_SPEED'] * gamerules['PLAYER_STRAFE_MODIFIER']
                player.z += math.cos(player.inputs['yaw']) * gamerules['PLAYER_SPEED'] * gamerules['PLAYER_STRAFE_MODIFIER']
            if 'd' in player.inputs['keyboard']:
                player.x += math.sin(player.inputs['yaw'] + math.pi / 2) * gamerules['PLAYER_SPEED'] * gamerules['PLAYER_STRAFE_MODIFIER']
                player.z += math.cos(player.inputs['yaw'] + math.pi / 2) * gamerules['PLAYER_SPEED'] * gamerules['PLAYER_STRAFE_MODIFIER']
            elif 'a' in player.inputs['keyboard']:
                player.x += math.sin(player.inputs['yaw'] - math.pi / 2) * gamerules['PLAYER_SPEED'] * gamerules['PLAYER_STRAFE_MODIFIER']
                player.z += math.cos(player.inputs['yaw'] - math.pi / 2) * gamerules['PLAYER_SPEED'] * gamerules['PLAYER_STRAFE_MODIFIER']
        sendPlayerDict = {}
        for sid in players:
            sendPlayerDict[sid] = players[sid].getDict()
        sio.emit('players', sendPlayerDict, broadcast=True)
        playersLock.release()

if __name__ == '__main__':
    sprint('server', 'Initializing...')
    sprint('server', 'Initializing variables...')
    players = {}
    playersLock = RLock()

    sprint('server', 'Initializing game loop...')
    gameLoopThread = sio.start_background_task(target=runGameLoop)

    sprint('server', f'Starting web server on port {PORT}')
    sio.run(app, host='0.0.0.0', port=PORT)
