#!/usr/bin/python3 -u

from flask import Flask, request
from flask_socketio import SocketIO
import mysql.connector
from dotenv import load_dotenv
# import noise

from datetime import datetime
from threading import RLock

load_dotenv()
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
sio = SocketIO(app, cors_allowed_origins='*')
db = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DATABASE']
)
cursor = db.cursor()

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

@sio.on('connect')
def connect():
    sprint('connect', f'{request.sid} {request.remote_addr}')
    print(app.config['MYSQL_HOST'])
    print(app.config['MYSQL_PASSWORD'])
    playersLock.acquire()
    players[request.sid] = Player(request.sid, 0, 0, 0)
    playersLock.release()

@sio.on('disconnect')
def disconnect():
    sprint('disconnect', f'{request.sid} {request.remote_addr}')
    # playersLock.acquire()
    # players.pop(request.sid)
    # playersLock.release()

def sprint(tag, text, timestamp=True):
    out = f'[{tag.upper()}'
    if timestamp:
        out += f' {datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")}'
    out += f'] {text}'
    print(out)

def runGameLoop():
    while True:
        sio.sleep(0.01)
        # playersLock.acquire()
        # for sid in players:
        #     player = players[sid]
        # sendPlayerDict = {}
        # for sid in players:
        #     sendPlayerDict[sid] = players[sid].getDict()
        # sio.emit('players', sendPlayerDict, broadcast=True)
        # playersLock.release()

if __name__ == '__main__':
    sprint('server', 'Initializing...')
    sprint('server', 'Initializing variables...')
    players = {}
    playersLock = RLock()

    sprint('server', 'Initializing game loop...')
    gameLoopThread = sio.start_background_task(target=runGameLoop)

    PORT = app.config['PORT']
    sprint('server', f'Starting web server on port {PORT}')
    sio.run(app, host='0.0.0.0', port=PORT)
