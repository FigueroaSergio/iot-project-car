from datetime import datetime
from pydantic import BaseModel,UUID4
from uuid import uuid4
from typing import List

from sensor import Sensor,Measure

class SensorManager(BaseModel):
    id:UUID4=uuid4()
    creation: datetime=datetime.now()
    sensors:List[Sensor]=[]
    stato:list[Measure]=[]
    

    def subscribe(self, sensor:Sensor):
        for c in self.sensors:
            if(c.id==sensor.id):
                return False
        self.sensors.append(sensor)
        return True
    
    def unsubscribe(self, sensor:Sensor):
        self.sensors = list(filter(lambda c:(not( c.id==sensor.id)),self.sensors))
        
    def _updateMeasures(self):
        self.stato = []
        for sensor in self.sensors:
            self.stato.append(sensor.getMeasure())

    def getStatus(self):
        self._updateMeasures()
        return  self.stato
    

    
