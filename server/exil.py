from flask import Flask, send_file, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
sio = SocketIO(app)

@app.route('/')
@app.route('/<path:path>')
def get(path='index.html'):
    return send_file(f'../public/{path}')

@sio.on('connect')
def connect():
    print(f'[CONNECT] {request.sid} {request.remote_addr}')

@sio.on('disconnect')
def disconnect():
    print(f'[DISCONNECT] {request.sid} {request.remote_addr}')

if __name__ == '__main__':
    sio.run(app, host='0.0.0.0', port=4000)
