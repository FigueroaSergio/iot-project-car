from pydantic import BaseModel,UUID4
from uuid import uuid4
from .car import Car

class Controller(BaseModel):
    id:UUID4=uuid4()
    car:Car

    def start(self):
        measures = self.car.getStatus()
        print(measures)

    def computeAction(self,):
        pass
    


