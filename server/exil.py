#!/usr/bin/python3 -u

import math
from datetime import datetime
from threading import RLock

import noise, json
from config import DevelopmentConfig
from flask import Flask, send_file, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
sio = SocketIO(app, cors_allowed_origins='*')

PORT = 4000

with open('config.json') as conf_file:
    CONF = json.load(conf_file)

class Player:
    def __init__(self, sid, x, y, z):
        self.sid = sid
        self.x = x
        self.y = y
        self.z = z
        self.xv = 0
        self.yv = 0
        self.zv = 0
        self.nv = 0
        self.sv = 0
        self.ev = 0
        self.wv = 0
        self.cl = 0
        self.grounded = True
        self.crouched = False
        self.chunkCooldown = 0
        self.inputs = {
            'keyboard': [],
            'actions': [],
            'pitch': 0,
            'yaw': 0
        }
        self.loadedChunks = []

    def getDict(self):
        return self.__dict__

class Chunk:
    def __init__(self, x, z): # X and Z are CHUNK COORDINATES, not 3D COORDINATES
        self.x = x
        self.z = z
        self.data = {}
        self.obj = {} # <-- to be used for models LATER!
        for xh in range(0, 51):
            for zh in range(0, 51):
                self.data[xh * 51 + zh] = getHeightMapAtPoint(x * 50 + xh, z * 50 + zh)

    def getDict(self):
        return self.__dict__

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, x, y):
        self.x += x
        self.y += y


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

def lerp(a, b, c):
    return a + (b - a) * c

def sig(a):
    return 1 / (1 + math.exp(-a))

def spia(r, x, y):
    c = []
    for i in range(r ** 2):
        c.append(spi(i, x, y))
    return c


def spi(x, a, b): # Dont ask me how i got this just accept that it works at generating spiral coordinates, probably inefficiently
    p = Vec2(a, b)
    d = 'n'
    o = False
    k = 1
    nk = 1
    while x > 0:
        if nk > 0:
            if d == 'n':
                p.y += 1
                nk -= 1
                if nk == 0:
                    d = 'e'
                    if o:
                        k += 1
                        o = False
                    else:
                        o = True
                    nk = k
            elif d == 'e':
                p.x += 1
                nk -= 1
                if nk == 0:
                    d = 's'
                    if o:
                        k += 1
                        o = False
                    else:
                        o = True
                    nk = k
            elif d == 's':
                p.y -= 1
                nk -= 1
                if nk == 0:
                    d = 'w'
                    if o:
                        k += 1
                        o = False
                    else:
                        o = True
                    nk = k
            elif d == 'w':
                p.x -= 1
                nk -= 1
                if nk == 0:
                    d = 'n'
                    if o:
                        k += 1
                        o = False
                    else:
                        o = True
                    nk = k
        x -= 1
    return p


def runGameLoop():
    while True:
        sio.sleep(0.01)
        playersLock.acquire()
        for sid in players: # 1: SEND PLAYER DATA OUT
            player = players[sid]
            LOCAL_SPEED_MODIFIER = 1 # Local Speed, used for things like walking, or hurt limbs
            if 'c' in player.inputs['keyboard']:
                LOCAL_SPEED_MODIFIER *= CONF['PLAYER_WALK_MODIFIER']
            if 'shift' in player.inputs['keyboard']:
                LOCAL_SPEED_MODIFIER *= CONF['PLAYER_CROUCH_MODIFIER']
                player.crouched = True
                player.cl = lerp(player.cl, 1, CONF['PLAYER_CROUCH_ANIMATION'])
            if 'j' in player.inputs['keyboard']:
                LOCAL_SPEED_MODIFIER *= 100
            if not player.grounded:
                LOCAL_SPEED_MODIFIER *= 1.2
            else:
                player.crouched = False
                player.cl = lerp(player.cl, 0, CONF['PLAYER_CROUCH_ANIMATION'])
            if 'w' in player.inputs['keyboard']:
                player.nv = lerp(player.nv, CONF['PLAYER_SPEED'] * LOCAL_SPEED_MODIFIER, CONF['PLAYER_ACCELERATION'])
            else:
                player.nv = lerp(player.nv, 0, CONF['PLAYER_DECELERATION'])
            if 's' in player.inputs['keyboard']:
                player.sv = lerp(player.sv, CONF['PLAYER_SPEED'] * LOCAL_SPEED_MODIFIER, CONF['PLAYER_ACCELERATION'])
            else:
                player.sv = lerp(player.sv, 0, CONF['PLAYER_DECELERATION'])
            if 'd' in player.inputs['keyboard']:
                player.ev = lerp(player.ev, CONF['PLAYER_SPEED'] * CONF['PLAYER_STRAFE_MODIFIER'] * LOCAL_SPEED_MODIFIER, CONF['PLAYER_ACCELERATION'])
            else:
                player.ev = lerp(player.ev, 0, CONF['PLAYER_DECELERATION'])
            if 'a' in player.inputs['keyboard']:
                player.wv = lerp(player.wv, CONF['PLAYER_SPEED'] * CONF['PLAYER_STRAFE_MODIFIER'] * LOCAL_SPEED_MODIFIER, CONF['PLAYER_ACCELERATION'])
            else:
                player.wv = lerp(player.wv, 0, CONF['PLAYER_DECELERATION'])
            player.xv = 0
            player.zv = 0
            player.xv += math.sin(player.inputs['yaw'] + math.pi) * player.nv
            player.zv += math.cos(player.inputs['yaw'] + math.pi) * player.nv
            player.xv += math.sin(player.inputs['yaw']) * player.sv
            player.zv += math.cos(player.inputs['yaw']) * player.sv
            player.xv += math.sin(player.inputs['yaw'] + math.pi / 2) * player.ev
            player.zv += math.cos(player.inputs['yaw'] + math.pi / 2) * player.ev
            player.xv += math.sin(player.inputs['yaw'] - math.pi / 2) * player.wv
            player.zv += math.cos(player.inputs['yaw'] - math.pi / 2) * player.wv
            ground = getHeightMapAtPoint(-player.x, player.z)
            if player.grounded:
                player.yv = 0
                player.y = ground
            if player.grounded and 'space' in player.inputs['keyboard']:
                player.yv = CONF['PLAYER_JUMP_FORCE']
                player.grounded = False
            if not player.grounded:
                player.yv -= CONF['GLOBAL_GRAVITY']
            player.x += player.xv
            player.z += player.zv
            player.y += player.yv
            if not player.grounded and player.y <= ground:
                player.grounded = True
                player.y = ground
                player.yv = 0
        sendPlayerDict = {}
        for sid in players:
            sendPlayerDict[sid] = players[sid].getDict()
        sio.emit('players', sendPlayerDict, broadcast=True)
        for sid in players:
            if players[sid].chunkCooldown <= 0:
                pchx = math.floor(-players[sid].x / 50)
                pchz = math.floor(players[sid].z / 50)
                chunksPacket = []
                for chc in spia(CONF['RENDER_DISTANCE'], pchx, pchz):
                    if f'{chc.x},{chc.y}' not in players[sid].loadedChunks and len(chunksPacket) < CONF['CHUNKS_PER_PACKET']:
                        chunksPacket.append(Chunk(chc.x, chc.y).getDict())
                        players[sid].loadedChunks.append(f'{chc.x},{chc.y}')

                sio.emit('chunks', chunksPacket, room=sid)
                players[sid].chunkCooldown = CONF['CHUNK_PACKET_DELAY']
            else:
                players[sid].chunkCooldown -= 1
        playersLock.release()

noiseOctaves = [
    {
        'freq': 0.00001,
        'amp': 4000,
        'offset': 0.5,
        'zDepth': 0,
    },
    {
        'freq': 0.00003,
        'amp': 1000,
        'offset': -0.2,
        'zDepth': 1000,
    },
    {
        'freq': 0.0005,
        'amp': 400,
        'offset': 0.2,
        'zDepth': 2000,
    },
    {
        'freq': 0.0008,
        'amp': 20,
        'offset': 0.5,
        'zDepth': 3000,
    },
    {
        'freq': 0.001,
        'amp': 200,
        'offset': 0,
        'zDepth': 4000,
    },
    {
        'freq': 0.001,
        'amp': 10,
        'offset': -0.4,
        'zDepth': 5000,
    },
    {
        'freq': 0.1,
        'amp': 0.2,
        'offset': 0,
        'zDepth': 6000,
    },
]

def getHeightMapAtPoint(x, y):
    h = 0
    for octave in noiseOctaves:
        h += ((noise.snoise3(x * octave['freq'], y * octave['freq'], octave['zDepth']) + octave['offset']) ** 2 * octave['amp'])
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
