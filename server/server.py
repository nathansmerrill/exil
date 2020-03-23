# import eventlet
# eventlet.monkey_patch()

from flask import Flask, send_file, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
sio = SocketIO(app)

@app.route('/')
@app.route('/<path:path>')
def index(path = 'index.html'):
    return send_file(f'../public/{path}')

@sio.on('connect')
def connect():
    print(f'[CONNECT] {request.sid}')

@sio.on('disconnect')
def disconnect():
    print(f'[DISCONNECT] {request.sid}')

@sio.on('ping')
def ping(data):
    print(f'[PING] {data}')

if __name__ == '__main__':
    # app.run(port=4000)
    sio.run(app, port=4000)
