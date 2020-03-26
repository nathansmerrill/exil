from flask import Flask, send_file, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
sio = SocketIO(app)

@app.route('/')
@app.route('/<path:path>')
def get(path='index.html'):
    return send_file(f'../public/{path}')

if __name__ == '__main__':
    sio.run(app, host='0.0.0.0', port=4000)
