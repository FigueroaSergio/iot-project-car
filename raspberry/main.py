import RPi.GPIO as GPIO
import time
from models.sensor import Sensor,Measure
from models.car import Car
from models.sensorManager import SensorManager
from models.controller import Controller


class SensorRasp(Sensor):
    trigger:int
    echo:int

    def __post_init__(self):
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def getMeasure(self):
        GPIO.output(self.trigger, GPIO.LOW)
        time.sleep(0.000002)
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger, GPIO.LOW)
        start_time=0
        end_time=0
        while not GPIO.input(self.echo) :
            start_time = time.time()

        while GPIO.input(self.echo):
            end_time = time.time()

        duration = end_time - start_time
        distance = duration * 17150 
        return Measure(distance=distance)


class CarRasp(Car):
    motor_pin1:int
    motor_pin2:int
    attiva_pin:int
    motor_pwm:GPIO.PWM=GPIO.PWM(2, 1000)
    def __post_init__(self):
        GPIO.setup(self.motor_pin1, GPIO.OUT)
        GPIO.setup(self.motor_pin2, GPIO.OUT)
        GPIO.setup(self.attiva_pin, GPIO.OUT)
        motor_pwm = GPIO.PWM(self.attiva_pin, 1000)  # Imposta la frequenza del PWM a 1kHz
        motor_pwm.start(0)

        

    def goForward(self):
        for i in range(0, 128):
            self.motor_pwm.ChangeDutyCycle(i / 2.55)
            GPIO.output(self.motor_pin1, GPIO.HIGH)
            GPIO.output(self.motor_pin2, GPIO.LOW)
            time.sleep(0.01)

    def goBackward(self):
        for i in range(0, 128):
            self.motor_pwm.ChangeDutyCycle(i / 2.55)
            GPIO.output(self.motor_pin2, GPIO.HIGH)
            GPIO.output(self.motor_pin1, GPIO.LOW)
            time.sleep(0.01)
    
    def stop(self):
        self.motor_pwm.ChangeDutyCycle(0)
        GPIO.output(self.motor_pin2, GPIO.LOW)
        GPIO.output(self.motor_pin1, GPIO.LOW)


class DummyController(Controller):
    def start(self):
        while True:
            measures= self.car.getStatus()
            near = False
            for measure in measures:
                if(measure.distance<20):
                    near = True
                    continue
            if(near):
                self.car.stop()
            else:
                self.car.goForward()
            


s1 = SensorRasp(trigger=2,echo=3)
s2 = SensorRasp(trigger=4,echo=5)
s3 = SensorRasp(trigger=7,echo=11)

sensors = SensorManager()
sensors.subscribe(s1)
sensors.subscribe(s2)
sensors.subscribe(s3)

car = CarRasp(
              velocity=2, 
              acceleration=10,
              sensors=sensors,
              motor_pin1=9,
              motor_pin2=10,
              attiva_pin=6)
controller=DummyController(car=car)

def main():
    controller.start()


if __name__ == "__main__":
    main()
