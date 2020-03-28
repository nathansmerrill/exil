from flask import Flask, send_file, request
from flask_socketio import SocketIO, emit
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
sio = SocketIO(app, cors_allowed_origins='*')

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
