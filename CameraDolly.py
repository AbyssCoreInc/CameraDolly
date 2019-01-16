from __future__ import print_function
import os
import subprocess
import sys
import time
import atexit
import threading
import random
from Configuration import *
from Camera import *
from Dolly import *
from MessageBroker import *
from LensHeater import *

threads = []
stepcount = 0
numsteps = 0
counter = 0

# create empty threads (these will hold the stepper 1 and 2 threads)
st1 = threading.Thread()

mh = Adafruit_MotorHAT()
#atexit.register(turnOffMotors)

def initiateThreads(datatrans,lensheater,configuration):
	t1 = threading.Thread(target=datatrans.worker)
	threads.append(t1)
	t1.start()
	
	t2 = threading.Thread(target=lensheater.worker)
	threads.append(t2)
	t2.start()
	
	print("started threads")

def getStepCount():
	return stepcount

def getCounter():
	return counter

def main():
	global stepcount
	global numsteps
	global counter
	conf = Configuration()
	conf.readConfiguration()

	images = conf.getDefaultImages()
			
	cam = Camera(conf)
	#	cam.initCamera()

	dolly = Dolly(conf,mh)
	lensHeater = LensHeater(mh,conf)

	mBroker = MessageBroker(conf.getMQTTURL(), conf.getMqttUsername(), conf.getMqttPassword,cam,dolly,lensHeater)
	mBroker.connect()
	cam.setMessageBroker(mBroker)
	lensHeater.setMessageBroker(mBroker)
	initiateThreads(mBroker,lensHeater,conf)
	
	print("main: going in the foreverloop")
	while (1):
		if (counter < images and dolly.isRunning == 1):
			counter = counter + 1
			# Move dolly
			dolly.moveDolly()
			# Wait for awhile
			time.sleep(conf.getStabisationBuffer())
			# Capture image
			cam.takePicture()
			mBroker.trasnmitPositionMessage(position, angle, counter)
			#statusMsq = "running"
			#mBroker.trasnmitdata(statusMsq, conf.getTopic()+"StatusMessage")
		else:
			statusMsq = "stopped"
			print("main: Dolly stopped sending message")
			mBroker.trasnmitdata(statusMsq, conf.getTopic()+"StatusMessage")
			counter = 0
			time.sleep(1)
	print("main: exiting the foreverloop")
	return 0

if __name__ == "__main__":
	sys.exit(main())
