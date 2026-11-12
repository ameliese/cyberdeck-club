from machine import Pin
from time import sleep

button1 = Pin(4, Pin.IN, Pin.PULL_UP)
button2 = Pin(5, Pin.IN, Pin.PULL_UP)

while True:

  if button1.value() == 0:
    print("Button 1 gedrückt")
  if button2.value() == 0:
    print("Button 2 gedrückt")
  sleep(0.1)