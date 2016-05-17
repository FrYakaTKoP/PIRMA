#!/usr/bin/env python
#
# 08-05-16 xx:xx cfr
#
import RPi.GPIO as GPIO
from time import sleep, time
import os, sys
import pygame.mixer 

## Configuration:
audioFile = "audio.wav"
armedFile = "armed.wav"
restTime = 10 # time in sec to rest before motion sensor gets enabled after playing 
restartHours = 4 # time in hours after the script restarts itself while armed w/o motion
sensorPin = 17
buttonPin = 18

## variables
startTime = time()
restartSec = restartHours * 3600


## set working dir to filepath
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

## Init Pygame.Mixer:
#pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
sndMain = pygame.mixer.Sound(audioFile)
sndArmed = pygame.mixer.Sound(armedFile)
sndArmed.set_volume(0.75)

## Setup GPIO to Input with Pulldown:
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensorPin, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(buttonPin, GPIO.IN, GPIO.PUD_DOWN)

## Restart Script
def restart():
    pygame.quit() ## quit pygame
    os.execv(sys.executable, [sys.executable] + sys.argv)


## Play Audio and rest before rearm
def playAudio():
    channelMain = sndMain.play() ## start playback 
    while channelMain.get_busy(): ## loop until audio file ends
        sleep(.500)  
    print('finished playing, rest %s seconds before rearm' % restTime)
    sleep(restTime) 
    restart()

    
## Arm PIR sensor:
def arm():          
    print('try to rearm...')  
    while GPIO.input(sensorPin):
        print('Sensor triggered, retry...')
        sleep(1)
    print ('armed...')
    sndArmed.play()
    sleep(0.2)         

## Callback function for Button Interrupt:
def buttonCallback(channel):
    print('Button pressed: restart')
    restart()
        
## Add Interrupt to Button:
GPIO.add_event_detect(buttonPin, GPIO.RISING, callback=buttonCallback, bouncetime=300)

## Initalize system:
arm()
armed = 1

## Run: 
try:
    while True:
        if armed == 1: ## Ignore motion while playing or resting
            if time() - startTime >= restartSec:
                ## restart after x hours
                print('armed more then %s hours, restarting' % restartHours)
                restart()
            if GPIO.input(sensorPin):                
                armed = 0 ## set playing status    
                print('motion detected: start playing...') 
                playAudio()
        sleep(.200)
        
finally:    
    #pygame.quit() ## quit pygame
    GPIO.cleanup() ## Cleanup GPIO config
