from datetime import datetime
from pydantic import BaseModel,Field,UUID4
from uuid import uuid4
from .sensorManager import SensorManager

class Car(BaseModel):
    id:UUID4=Field(default_factory=lambda: uuid4())
    velocity:float
    acceleration:float
    
    angle:int=Field(default=90,ge=0,lt=360)
    creation: datetime=datetime.now()
    sensors: SensorManager

    def getStatus(self):
        print('Ready sensors...')
        return self.sensors.getStatus()
    
    def goForward(self):
        pass

    def goBackward(self):
        pass
    
    def stop(self):
        pass
    
    def setAngle(self, angle:float):
        pass

