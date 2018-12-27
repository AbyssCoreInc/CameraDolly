from __future__ import print_function

import logging
import os
import subprocess
import sys
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import time
import atexit
import threading
import random
import Configuration

threads = []

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

def initiateThreads(datatrans,configuration):
	sm = CameraManager(configuration)
	ds = DataObserver(datatrans,sm)
	
	t1 = threading.Thread(target=ds.worker)
	threads.append(t1)
	t1.start()
	t2 = threading.Thread(target=sm.worker)
	threads.append(t2)
	t2.start()
	
	t3 = threading.Thread(target=sm.lora.worker)
	threads.append(t3)
	t3.start()
	print("started threads")



def main():
	
	conf = Configuration()
	conf.readConfiguration()
	
	myStepper1 = mh.getStepper(200, 1)      # 200 steps/rev, motor port #1
	myStepper1.setSpeed(conf.getStepperSpeed())          # 30 RPM

	numsteps = conf.getStepsPerFrame()
	images = conf.getDefaultImages()
	
	camera = Camera()
	camera.initCamera()
	
	mBroker = MessageBroker(camera)
	
	direction = Adafruit_MotorHAT.BACKWARD
	style = Adafruit_MotorHAT.DOUBLE

	counter = 0
	while (1):
		if (counter < images and camera.running == 1):
			counter = counter + 1
			# Move dolly
			myStepper1.step(numsteps, direction, style)
			# Wait for awhile
			time.sleep(1)
			# Capture image
			camera.takePicture()
		else:
			counter = 0
	
	return 0

if __name__ == "__main__":
	sys.exit(main())
