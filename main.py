from models.car import Car
from models.sensorManager import SensorManager
from models.sensor import Sensor


def main():
    s1= Sensor()
    s2= Sensor()
    s3=Sensor()
    sensors = SensorManager()
    sensors.subscribe(s1)
    sensors.subscribe(s2)
    sensors.subscribe(s3)
    car = Car(velocity=2, acceleration=10,sensors=sensors)

    print(car.model_dump())


if __name__ == "__main__":
    main()
