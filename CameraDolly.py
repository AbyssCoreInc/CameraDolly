from __future__ import print_function
import os
import subprocess
import sys
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import time
import atexit
import threading
import random
from Configuration import *
from Camera import *
from MessageBroker import *
from LensHeater import *

threads = []
stepcount = 0
numsteps = 0

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT()

# create empty threads (these will hold the stepper 1 and 2 threads)
st1 = threading.Thread()

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.BRAKE)
    mh.getMotor(2).run(Adafruit_MotorHAT.BRAKE)
    mh.getMotor(3).run(Adafruit_MotorHAT.BRAKE)
    mh.getMotor(4).run(Adafruit_MotorHAT.BRAKE)

atexit.register(turnOffMotors)

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

def sendStepSize():
	return numsteps

def main():
	global stepcount
	global numsteps

	conf = Configuration()
	conf.readConfiguration()
	
	myStepper1 = mh.getStepper(200, 1)      # 200 steps/rev, motor port #1
	myStepper1.setSpeed(conf.getStepperSpeed())          # 30 RPM
	
	numsteps = conf.getStepsPerFrame()
	images = conf.getDefaultImages()
			
	cam = Camera(conf)
	cam.initCamera()

	direction = Adafruit_MotorHAT.BACKWARD
	style = Adafruit_MotorHAT.DOUBLE

	#start lens warming on PWM0 on motorhat
	#mh.setPin(0,0)
	lensHeater = LensHeater(mh)

	mBroker = MessageBroker(conf.getMQTTURL(), conf.getMqttUsername(), conf.getMqttPassword,cam,lensHeater)
	mBroker.connect()
	cam.setMessageBroker(mBroker)
	
	initiateThreads(mBroker,lensHeater,conf)
	counter = 0
	while (1):
		if (counter < images and cam.running == 1):
			counter = counter + 1
			# Move dolly
			myStepper1.step(numsteps, direction, style)
			stepcount = stepcount+numsteps
			# Wait for awhile
			time.sleep(1)
			# Capture image
			cam.takePicture()
			statusMsq = "Image "+str(counter)+" of "+str(images)+" taken"
			mBroker.trasnmitdata(statusMsq, conf.getTopic()+"StatusMessage")
			statusMsq = "running"
			mBroker.trasnmitdata(statusMsq, conf.getTopic()+"StatusMessage")
		else:
			statusMsq = "stopped"
			mBroker.trasnmitdata(statusMsq, conf.getTopic()+"StatusMessage")
			counter = 0
			time.sleep(1)
	
	return 0

if __name__ == "__main__":
	sys.exit(main())
