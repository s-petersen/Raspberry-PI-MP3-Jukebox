#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Paul van Veen, mod by Scott Petersen

import RPi.GPIO as GPIO
import os, sys, time

#contants and literals
SELECTION_LETTERS=("V","U","T","S","R","Q","P","N","M","L","K","J","H","G","F","E","D","C","B","A")
WALLBOX=20
dirsong=("Blue")
#>>>these constants can be changed to fit the characteristics of your wallbox
MAXMIMUM_GAP=2
MINIMUM_PULSE_GAP_WIDTH=0.013
LETTER_NUMBER_GAP=0.2
song="error"                                                                
#set up IO port for input
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(WALLBOX, GPIO.IN)
GPIO.setup(9, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)


#this function tests if a pulse or gap is wide enough to be registered
#this is needed for two reasons. 1) Sometimes the wallbox will generate an errant pulse
#which will cause errors if interpretted as a proper contact pulse 2) because of the
#way that I have tapped the wallbox pulses, there will be short gaps inside each pulse
#that need to be ignored

def state_has_changed(starting_state):
    starting_time = time.time()
    elapsed_time = 0

    for i in range (200):
        if not GPIO.input(WALLBOX) != starting_state: 
            elapsed_time = time.time() - starting_time
            print ("check time recorded: %.3f" %elapsed_time)
            return False
    return True
        
#this function is called as soon as the main loop determines that a train of pulses
#has started.  It begins by counting the number pulses, then when it encounters a larger
#gap, it starts incrementing the letters.  If your wallbox uses the opposite order
#you will need to change this.  Also the final calculation of the track may need to be changed
#as some boxes have additional pulses at either the start or the end of the train
#once it encounters a gap over a pre-determined maxmimum we know that the rotator arm
#has stopped and we calculate the track 

def calculate_track():
    global song                                                 # ***** added *******
    global dirsong
    state = True
    count_of_number_pulses = 9 #since we are in the first pulse
    count_of_letter_pulses = 0
    length_of_last_gap = 0
    first_train = True
    time_of_last_gap = time.time()
    
    while length_of_last_gap < MAXMIMUM_GAP:
        if not GPIO.input(WALLBOX) != state: 
            
            if state_has_changed(not state): # state has changed but check it is not anomaly
                state = not state # I use this rather than the GPIO value just in case GPIO has changed - unlikely but possible
                if state: #indicates we're in a new pulse
                    length_of_last_gap = time.time() - time_of_last_gap 
                    print ("Last gap: %.3f" %length_of_last_gap)

                    if length_of_last_gap > LETTER_NUMBER_GAP: # indicates we're into the second train of pulses
                        first_train = False

                    if first_train:
                        if length_of_last_gap > MINIMUM_PULSE_GAP_WIDTH:  count_of_number_pulses -= 1
                    else:
                         count_of_letter_pulses +=1
                         if count_of_number_pulses > 9: count_of_number_pulses = 9
                         if count_of_letter_pulses > 20: count_of_letter_pulses = 20
                else: #indicates we're in a new gap
                    time_of_last_gap = time.time()
        else:
            length_of_last_gap = time.time() - time_of_last_gap #update gap length and continue to poll
    song =  SELECTION_LETTERS[count_of_letter_pulses -1] + str((count_of_number_pulses))

    print (dirsong+","+song)
    
    with open('/home/pi/Desktop/Queue.csv',"a") as f:
           f.write(dirsong+","+song+"\n")
#while True:  
    if  dirsong == "Blue" and song == "V8":
         dirsong = "Red"
                  
    elif dirsong == "Red" and song == "V8":
         dirsong = "Blue"
                  
  
    if   dirsong == "Blue":
         GPIO.output(9,0)
         GPIO.output(10,1)
    if   dirsong == "Red":
         GPIO.output(9,1)
         GPIO.output(10,0)
         
                    
#this is the main loop.  We poll the GPIO port until there is a pulse.
#sometimes there can be random pulses, or a spike when the rotor arm starts to move 
#so before trying to decode the pulse train I check that
#the pulse is long enough to indicate a contact on the selector arm

while True:
    if  GPIO.wait_for_edge(WALLBOX, GPIO.BOTH):
         if state_has_changed(True):
            track = calculate_track()
        
        
    else:
         if  dirsong == "Blue" and song == "V8":
             dirsong = "Red"
                  
         elif dirsong == "Red" and song == "V8":
              dirsong = "Blue"
                  
  
    if   dirsong == "Blue":
             GPIO.output(9,0)
             GPIO.output(10,1)
    if   dirsong == "Red":
            GPIO.output(9,1)
            GPIO.output(10,0)             
             
            time.sleep(.001)
            print ("--> Pulse ignored")
