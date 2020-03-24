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
users = db['users']

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
'''
0: Success
1: Username wrong
2: Password wrong
'''
@sio.on('login')
def login(data):
    sprint('LOGIN', data)
    user = users.find_one({'username': data['username']})
    if user is None:
        emit('login', 1)
    else:
        if bcrypt.check_password_hash(user['password'], data['password']):
            emit('login', 0)
        else:
            emit('login', 2)

'''
0: Success
1: User already exists
2: Password is blank
'''
@sio.on('register')
def register(data):
    sprint('SIGNUP', data)
    if users.find_one({'username': data['username']}) is not None:
        emit('register', 1)
    elif data['password'] == '':
        emit('register', 2)
    else:
        users.insert_one({
            'username': data['username'],
            'password': bcrypt.generate_password_hash(data['password']).decode('UTF-8')
        })
        emit('register', 0)

if __name__ == '__main__':
    sprint('SERVER', 'Initializing...')
    sio.run(app, port=4000)
    # app.run(port=4000)
