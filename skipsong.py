#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN)

while True:
    if      GPIO.input(2)==0:

        os.system("sudo pkill -f mplayer")
        print ("song skipped")
                          
        time.sleep(1)
    else:
        time.sleep(.1)