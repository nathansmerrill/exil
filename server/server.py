from flask import Flask, send_file, request
from flask_socketio import SocketIO, emit
from flask_bcrypt import Bcrypt
from pymongo import MongoClient

from datetime import datetime

app = Flask(__name__)
sio = SocketIO(app)
# bcrypt.generate_password_hash(pw).decode('UTF-8')
# bcrypt.check_password_hash(hash, candidate)
bcrypt = Bcrypt(app)

client = MongoClient('mongodb://localhost:27017')
db = client['exil']

def sprint(tag, message, timestamp=True):
    out = f'[{tag}'
    if timestamp:
        out += f' {datetime.now().strftime("%d-%b-%Y %-I:%M:%S %p")}'
    out += f'] {message}'
    print(out)

@app.route('/')
@app.route('/<path:path>')
def index(path='index.html'):
    return send_file(f'../public/{path}')

@sio.on('connect')
def connect():
    sprint('CONNECT', request.sid)

@sio.on('disconnect')
def disconnect():
    sprint('DISCONNECT', request.sid)

if __name__ == '__main__':
    sprint('SERVER', 'Initializing...')
    sio.run(app, port=4000)
    # app.run(port=4000)
