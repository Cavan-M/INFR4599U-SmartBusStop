from I2C_LCD import lcd
import dht11
import RPi.GPIO as GPIO
from time import sleep


# Simple Pin control
class SimplePIN:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)


relay = SimplePIN(26)

while True:
    temperature = dht11.main()
    if temperature != None and temperature < 25:
        relay.on()
    elif temperature != None and temperature > 24:
        relay.off()
    print (temperature)
    sleep(3)