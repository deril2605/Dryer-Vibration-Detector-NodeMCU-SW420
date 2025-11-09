# main.py -- put your code here!
from machine import Pin
import time

led = Pin(2, Pin.OUT)
for i in range(10):
    led.value(0)
    time.sleep(0.5)
    led.value(1)
    time.sleep(0.5)
