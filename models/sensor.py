from datetime import datetime
from pydantic import BaseModel,Field,UUID4
from typing import Any,Optional
from uuid import uuid4

class Sensor(BaseModel):
    id:UUID4=Field(default_factory=lambda: uuid4())
    creation: datetime=datetime.now()
    distance:float=Field(default=0)
    position:str=Field(default='')
    def model_post_init(__context: Any) -> None:
        print('post init')

    def getMeasure(self):
        return Measure(distance=self.distance,position=position,id=self.id)

class Measure(BaseModel):
    date: datetime= datetime.now()
    distance: float
    position:str=''
    id:UUID4