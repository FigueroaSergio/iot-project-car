import RPi.GPIO as GPIO
#import pigpio
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo
import time
from typing import Any

# from pydantic import Any

from models.sensor import Sensor,Measure
from models.car import Car
from models.sensorManager import SensorManager
from models.controller import Controller

# pi = pigpio.pi("pi",8889)


class SensorRasp(Sensor):
    trigger:int
    echo:int

    def __init__(self, **data: Sensor):
        super().__init__(**data)
        print('Init sensor...')
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def getMeasure(self):
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger, GPIO.LOW)

        start_time = time.time()
        end_time = time.time()

        while GPIO.input(self.echo)==0 :
            start_time = time.time()

        while GPIO.input(self.echo)==1:
            end_time = time.time()

        duration = end_time - start_time
        distance = (duration * 34300) / 2
        time.sleep(0.5)
        return Measure(distance=distance,position=self.position, id=self.id)


class CarRasp(Car):
    motor_pin1:int
    motor_pin2:int
    attiva_pin:int
    servo_pin:int
    motor_pwm: Any
    servo: Any
    def __init__(self, **data):
        super().__init__(**data)
        print('Init Motors...')
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.motor_pin1, GPIO.OUT)
        GPIO.setup(self.motor_pin2, GPIO.OUT)
        GPIO.setup(self.attiva_pin, GPIO.OUT)

        # CONFIG pwm for speed
        self.motor_pwm = GPIO.PWM(self.attiva_pin, 1000)  # Imposta la frequenza del PWM a 1kHz
        self.motor_pwm.start(0)

        # CONFIG servo
        print('Init Servo...')
        GPIO.setup(self.servo_pin, GPIO.OUT)
        #self.servo = GPIO.PWM(self.servo_pin, 50)  # Imposta la frequenza del PWM a 50Hz
        #self.servo.start(self._angle_to_percent(self.angle))
        factory = PiGPIOFactory()       #obbligatorio per ridurre i jitter
        self.servo = AngularServo(self.servo_pin, min_angle=50, max_angle=150, initial_angle=110, pin_factory=factory)
        # la guida seguita diceva di impostare min_pulse_width=0.0005, max_pulse_width=0.0024, ma dipende dal servo

    def goForward(self):
        print('Go Forward')
        for i in range(0, 256):
            self.motor_pwm.ChangeDutyCycle(i / 2.55)
            GPIO.output(self.motor_pin1, GPIO.HIGH)
            GPIO.output(self.motor_pin2, GPIO.LOW)
            time.sleep(0.01)

    def goBackward(self):
        print('Go backward')
        for i in range(0, 256):
            self.motor_pwm.ChangeDutyCycle(i / 2.55)
            GPIO.output(self.motor_pin2, GPIO.HIGH)
            GPIO.output(self.motor_pin1, GPIO.LOW)
            time.sleep(0.01)
    
    def stop(self):
        print('Stop')
        self.motor_pwm.ChangeDutyCycle(0)
        GPIO.output(self.motor_pin2, GPIO.LOW)
        GPIO.output(self.motor_pin1, GPIO.LOW)
        time.sleep(0.01)
        
    def setAngle(self, angle:float):
        if angle>150:       #150
            angle=150       #150
        if angle<50:        #40
            angle=50        #40
        #percent = self._angle_to_percent(angle)
        #print(f'Set angle {angle} = {percent} percent')
        print(f'Set angle {angle}')

        GPIO.output(self.servo_pin, GPIO.HIGH)
        #self.servo.ChangeDutyCycle(percent)
        self.servo.angle=angle
        GPIO.output(self.servo_pin, GPIO.LOW)
        time.sleep(0.01)

    def _angle_to_percent(self, angle:float):
        duty= angle / 18 + 2.5
        return duty


class DummyController(Controller):
    def start(self):
        while False:
            measures= self.car.getStatus()
            print(measures)
            near = False
            for measure in measures:
                if(measure.distance<20):
                    near = True
                    continue
            if(near):
                self.car.stop()
            else:
                self.car.goForward()
            


# s2 = SensorRasp(trigger=4,echo=5)
# s3 = SensorRasp(trigger=7,echo=11)


# sensors.subscribe(s2)
# sensors.subscribe(s3)



def main():
    
    try:
        s1 = SensorRasp(trigger=27,echo=22, position='left')
        #s2 = SensorRasp(trigger=5,echo=6, position='right')
        #print(s2.getMeasure())
        print(s1.getMeasure())
        # s1 = SensorRasp(trigger=2,echo=3, position='Front')
        sensors = SensorManager()
        sensors.subscribe(s1)
        # sensors.subscribe(s2)
        car = CarRasp(
              velocity=2, 
              acceleration=10,
              sensors=sensors,
              motor_pin1=14,
              motor_pin2=15,
              attiva_pin=12,
              servo_pin=13)
        car.goBackward()
        #car.goForward()
        #car.stop()
        #car.setAngle(0)
        car.setAngle(90)
        #car.setAngle(180)
        #car.setAngle(0)
        status=car.getStatus()
        print(status)

        controller=DummyController(car=car)
        controller.start()
        
    finally:
        GPIO.cleanup()
    


if __name__ == "__main__":
    main()
