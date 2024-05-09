from datetime import datetime
from pydantic import BaseModel,Field,UUID4
from uuid import uuid4
from sensorManager import SensorManager

class Car(BaseModel):
    id:UUID4=uuid4()
    velocity:float
    acceleration:float
    
    angle:int=Field(default=0,ge=0,lt=360)
    creation: datetime=datetime.now()
    sensors: SensorManager

    def getStatus(self):
        return self.sensors.getStatus()

