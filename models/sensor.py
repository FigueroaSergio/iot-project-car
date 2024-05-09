from datetime import datetime
from pydantic import BaseModel,Field,UUID4
from uuid import uuid4

class Sensor(BaseModel):
    id:UUID4=uuid4()
    creation: datetime=datetime.now()
    distance:float=Field(default=0)

    def getMeasure(self):
        return Measure(distance=self.distance)

class Measure(BaseModel):
    date: datetime= datetime.now()
    distance: float