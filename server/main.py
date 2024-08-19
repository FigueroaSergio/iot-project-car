# eventlet.monkey_patch()
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaRelay
from fastapi.responses import HTMLResponse

from fastapi.staticfiles import StaticFiles

import logging
import asyncio
import time
import uvicorn
from image import frame_processor
from editor import Editor

app = FastAPI(reload=True)

sio =socketio.AsyncServer(async_mode='asgi',cors_allowed_origins='*')
app.mount('/socket.io', socketio.ASGIApp(sio))
app.mount("/static", StaticFiles(directory="./templates"), name="static")

# Set the logging level (adjust as needed)


pc:RTCPeerConnection = None
relay = MediaRelay()

class VideoTransformTrack(VideoStreamTrack):
    editor = None

    def __init__(self, track,by):
        super().__init__()
        self.track = track
        self.by = by

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        try:
            display=True
            if VideoTransformTrack.editor is None:
                VideoTransformTrack.editor = Editor(img,{
                    'step':5
                },display)
            
            processed_img = await asyncio.get_event_loop().run_in_executor(None, VideoTransformTrack.editor.process, img)
            angle = VideoTransformTrack.editor.curr_steering_angle
            # Display the processed image using OpenCV
            if(display):    
                cv2.imshow(f'view-{self.by}', processed_img)
            cv2.waitKey(1)  # Allow OpenCV to process events
            pass
        except Exception as e:
            print(e)
        return frame
       

@app.get('/', response_class=HTMLResponse)
def index():
    with open("templates/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@sio.on('broadcaster')
async def broadcaster(id):
    
    print('broadcaster',id)
    await sio.emit('broadcaster')

# @sio.event
# def frame(data):
#     print('frame')
#     sio.emit('frame',data,broadcast=True)

@sio.on('watcher')
async def watcher(id):
    print('Received watcher event', id)
    await sio.emit('watcher', id)
    

@sio.on('offer')
async def offer(id, data):
    print('Received offer event',id)
    if(data['to']=='server'):
        await stream(id, data)
        return
    await sio.emit('offer', data)
    return

@sio.on('answer')
async def answer(id,data):
    print('Received answer event',id)
    await sio.emit('answer', data)

@sio.on('candidate')
async def on_candidate(id,candidate):
    print('Received candidate event')
    await sio.emit('candidate', candidate)

# @socketio.on('disconnectPeer')
# async def on_disconnect():
#     pc = pcs.get()
#     await pc.close()
#     pcs.discard(pc)


async def stream(id,data):
    localDescription=data['offer']
    global pc
    if(pc!=None):
        del pc
    print('Received stream')
    offer = RTCSessionDescription(sdp=localDescription['sdp'], type=localDescription['type'])
    pc = RTCPeerConnection()
    @pc.on("icecandidate")
    def on_icecandidate(event):
        if event.candidate:
            socketio.emit('candidate', {'candidate': event.candidate})
    @pc.on("track")
    def on_track(track):
        print('track', track.kind)
        if track.kind == "video":
            pc.addTrack(VideoTransformTrack(track,id))
    print("Setting remote description...")
    await pc.setRemoteDescription(offer)
    print("Remote description set.")
    try:
        print("Creating answer...")
        answer = await pc.createAnswer()
        if not answer:
            print('No answer created')
            return
        print("Answer created.")
        await pc.setLocalDescription(answer)
    except Exception as e:
        logging.error(f"Error processing data: {e}")

    try:
        print('Answering')
        await sio.emit('answer', {'answer':{'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type},'from':'server', 'to':id})
    except Exception as e:
        print(f"Error in stream function: {e}")

if __name__ == '__main__':
    
    uvicorn.run(app, host='0.0.0.0',port=5000,
                ssl_keyfile="./key.pem",
                ssl_certfile="./cert.pem",
                )
