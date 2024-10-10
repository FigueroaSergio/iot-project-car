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
from rasp import SensorRasp, CarRasp, SensorManager
from db import create_db_and_table, insert_coordinates
from threading import Thread




app = FastAPI(reload=True)

sio =socketio.AsyncServer(async_mode='asgi',cors_allowed_origins='*')
app.mount('/socket.io', socketio.ASGIApp(sio))
app.mount("/static", StaticFiles(directory="./templates"), name="static")
create_db_and_table()


# Set the logging level (adjust as needed)


pc:RTCPeerConnection = None
relay = MediaRelay()
drivemode = False
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
                    'step':4,
                    'Point-1-y':40,
                    'Point-2-y':40,
                    'Point-0-y':95,
                    'Point-3-y':95
                }, display)
            
            VideoTransformTrack.counterPaolo=0
            
            processed_img = await asyncio.get_event_loop().run_in_executor(None, VideoTransformTrack.editor.process, img)

            if drivemode:
                angle = VideoTransformTrack.editor.curr_steering_angle
                #sio.emit('gira', {'id' : id, 'angle' : angle})
                #print("STO PER SETTARE L'ANGOLO!!!")
                car.setAngle(angle)

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


async def verifyDistance():
    while True:
        misura = car.getStatus()
        if(misura[len(misura)-1].distance<30):      #15
            car.stop()
        #print(f"STO LEGGENDO MISURA:")
        await sio.emit('distance_update', {'distance': misura[0].distance})
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(verifyDistance())

@sio.on('cambioguida')
async def cambioguida(sid, data):
    global drivemode
    drivemode = data.get('autoDrive', False)
    mode = "autonoma" if drivemode else "manuale"
    print(f"Modalità di guida cambiata: {mode}")
    
@sio.on('broadcaster')
async def broadcaster(id):
    
    print('broadcaster',id)
    await sio.emit('broadcaster')

@sio.on('gira')
def gira(id,angle):
    car.setAngle(angle)
    print('Angolo impostato', angle)

@sio.on('go_forward')
def go_forward(id):
    car.goForward()

    print('Car is moving forward')

@sio.on('go_backward')
def go_backward(id):
    car.goBackward()
    print('Car is moving backward')

@sio.on('stop')
def stop(id):
    car.stop()
    print('Car has stopped')
    
@sio.on('distance_update')
def distance_update(id,misura):
    sio.emit('distance_update', {'distance': misura})
    print("ciao")
    
locations = {}
@sio.on('location')
async def location(sid, data):
    try:
        print(f"Location data received from {sid}: {data}")
        locations[sid] = data
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if latitude is not None and longitude is not None:
            insert_coordinates(latitude, longitude)
        await sio.emit('locationUpdate', {'id': sid, **data})
    except:
        print("ERRORE LOCATION")

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

car = None

if __name__ == '__main__':
   

    sensors = SensorManager()
    # s2 = SensorRasp(trigger=5,echo=6, position='right')
    # print(s2.getMeasure())
    # sensors.subscribe(s2)

    s1 = SensorRasp(trigger=2,echo=3, position='front')
    print(s1.getMeasure())
    sensors.subscribe(s1)



    car = CarRasp(
              # trigger=2, echo=3 --> 3 e 5
              velocity=2, 
              acceleration=10,
              sensors=sensors,
              motor_pin1=9,     # 21
              motor_pin2=10,    # 19
              attiva_pin=6,     # 31
              servo_pin=13)     # 33
    car.setAngle(90)

    uvicorn.run(
            app=app, 
            host='0.0.0.0',
            port=5000,
            ssl_keyfile="./key.pem",
            ssl_certfile="./cert.pem",
        )
