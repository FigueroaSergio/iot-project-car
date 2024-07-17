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

import uvicorn
from image import frame_processor
from editor import Editor

app = FastAPI(reload=True)

sio =socketio.AsyncServer(async_mode='asgi',cors_allowed_origins='*')
app.mount('/socket.io', socketio.ASGIApp(sio))
app.mount("/static", StaticFiles(directory="./templates"), name="static")

# Set the logging level (adjust as needed)


pcs:set[RTCPeerConnection] = set()
relay = MediaRelay()

class VideoTransformTrack(VideoStreamTrack):
    def __init__(self, track):
        super().__init__()  # don't forget this!
        self.track = track
        self.editor =None

    async def recv(self):
        frame = await self.track.recv()
        # Convert frame to OpenCV format
        img = frame.to_ndarray(format="bgr24")
        # Process frame (display it)
        try:
            if(self.editor is None):
                self.editor = Editor(img)
            # self.editor.setImage(img)

            s =self.editor.process(img)
            cv2.imshow('view-1',s)      
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print('s')
                pass
        # Introduce a delay to control the frequency
        # await asyncio.sleep(0.1)  # Adjust the delay time (in seconds) as needed
        # Return the frame unchanged
        except Execption as e:
            print(e)
        return frame

@app.get('/', response_class=HTMLResponse)
def index():
    with open("templates/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get('/controller', response_class=HTMLResponse)
def viewer():
    with open("templates/watcher.html") as f:
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
async def offer(id,localDescription):
    print('Received offer event',id)
    await sio.emit('offer', localDescription)

# @sio.event
# def connect():
#     print('connection')
#     client_id = str(uuid4())  # Generar un ID único
#     emit('assign_id', {'id': client_id})

@sio.on('answer')
async def answer(id,data):
    print('Received answer event',id)
    await sio.emit('answer', {'answer':data,'id':id})

@sio.on('candidate')
async def on_candidate(id,candidate):
    print('Received candidate event')
    await sio.emit('candidate', candidate)

# @socketio.on('disconnectPeer')
# async def on_disconnect():
#     pc = pcs.get()
#     await pc.close()
#     pcs.discard(pc)


@sio.on('stream')
async def stream(id,localDescription):

  
    global pcs
    print('Received stream')
    offer = RTCSessionDescription(sdp=localDescription['sdp'], type=localDescription['type'])
    pc = RTCPeerConnection()
    pcs.add(pc)
    @pc.on("icecandidate")
    def on_icecandidate(event):
        if event.candidate:
            socketio.emit('candidate', {'candidate': event.candidate})
    @pc.on("track")
    def on_track(track):
        print('track', track.kind)
        if track.kind == "video":
            pc.addTrack(VideoTransformTrack(track))
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
        print('answering')
        await sio.emit('answer', {'answer':{'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type},'id':'server'})
    except Exception as e:
        print(f"Error in stream function: {e}")

if __name__ == '__main__':
    
    uvicorn.run(app, host='0.0.0.0',port=5000,
                ssl_keyfile="./key.pem",
                ssl_certfile="./cert.pem",
                )

# @socketio.on('stream')
# def stream(localDescription):
#     app.logger.debug(f"Received data from client: {localDescription}")

# async def stream(localDescrition):
#     # print(localDescrition)
#     app.logger.debug(f"Received data from client: {localDescrition}")
#     # ... your processing code ...
#     async def process_stream(localDescrition):
#         global pcs
#         print('Recived stream')  
#         emit('answer','answer',broadcast=True)
#         # print(localDescrition)  
#         offer = RTCSessionDescription(sdp=localDescrition['sdp'], type=localDescrition['type'])
#         pc = RTCPeerConnection()
#         pcs.add(pc)

#         @pc.on("icecandidate")
#         def on_icecandidate(event):
#             if event.candidate:
#                 socketio.emit('candidate', {'candidate': event.candidate})

#         @pc.on("track")
#         def on_track(track):
#             print('track',track.kind)
#             if track.kind == "video":
#                 pc.addTrack(VideoProcessorTrack(track))

    
#         await pc.setRemoteDescription(offer)
#         answer = await pc.createAnswer()
#         if(not answer):
#             print('no answer')
#             return
#         await pc.setLocalDescription(answer)
#         return answer
   
#     try:
#         response = await process_stream(localDescrition)
#         print('answering')
#         emit('answer',response,broadcast=True)    
#     except Exception as e:
#         print(f"Error processing data: {e}")
#         emit('my_error', {'message': 'An error occurred during processing.'})


