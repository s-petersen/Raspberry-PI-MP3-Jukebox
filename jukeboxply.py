#!/usr/bin/env python
# Thanks to Gordon77! on www,raspberrypi.org/forums
import os
import time

def playSong(dirname, songname): 
         os.system("sudo mplayer /boot/jukebox/jukeboxmusic/" + dirname + "/" + songname + "/" + "*.mp3") 

while True:
    time.sleep (.1)
    while os.path.getsize('/home/pi/Desktop/Queue.csv') > 0:
        
        tunes = []        
        with open('/home/pi/Desktop/Queue.csv',"r") as textobj:
           line = textobj.readline()
           while line:
              tunes.append(line.strip())
              line = textobj.readline()
        dirname = (tunes[0].split(',')[0])
        songname = (tunes[0].split(',')[1])
        del tunes[0]
        with open('/home/pi/Desktop/Queue.csv',"w") as f:
            for item in tunes:
                f.write("%s\n" % item)
        playSong(dirname,songname)
    