import cv2
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaRelay
import asyncio

from uuid import uuid4

app = Flask(__name__)
socketio = SocketIO(app,cors_allowed_origins="*")

pcs = {}
relay = MediaRelay()

class VideoTransformTrack(VideoStreamTrack):
    def __init__(self, track):
        super().__init__()  # don't forget this!
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        
        # Process the frame with OpenCV
        img = frame.to_ndarray(format="bgr24")
        height, width, _ = img.shape
        cv2.rectangle(img, (0, 0), (width, height), (0, 255, 0), 10)
        
        # Convert back to video frame
        new_frame = frame.from_ndarray(img, format="bgr24")
        return new_frame

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/controller')
def viewer():
    return render_template('watcher.html')

@socketio.on('broadcaster')
def broadcaster():
    print('broadcaster')
    emit('broadcaster',broadcast=True)

@socketio.on('watcher')
def watcher(id):
    print('Received watcher event')
    emit('watcher',id,broadcast=True)
    

@socketio.on('offer')
def on_offer(localDescription):
    print('Received offer event')
    emit('offer', localDescription, broadcast=True)

@socketio.on('connect')
def connect():
    print('connection')
    client_id = str(uuid4())  # Generar un ID único
    emit('assign_id', {'id': client_id})

@socketio.on('answer')
def on_answer(localDescription):
    print('Received answer event')
    emit('answer', localDescription, broadcast=True)

@socketio.on('candidate')
def on_candidate(candidate):
    print('Received candidate event')
    emit('candidate', candidate, broadcast=True)

@socketio.on('disconnectPeer')
async def on_disconnect():
    pc = pcs.get()
    await pc.close()
    pcs.discard(pc)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000,debug=True)
