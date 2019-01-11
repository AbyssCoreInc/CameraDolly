import logging
import time
from Configuration import *
from MessageBroker import *
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

class Dolly:
	def __init__(self, configuration,motorhat):
		# create a default object, no changes to I2C address or frequency
		self.mh = motorhat
		self.config = configuration
		self.running = 0
		self.stepsPerRev = conf.getStepsPerRev()
		self.myStepper1 = mh.getStepper(stepsPerRev, 1)      # 200 steps/rev, motor port #1
		self.myStepper1.setSpeed(conf.getStepperSpeed())
	
		self.stepcount = 0
		self.anglecount = 0
		self.numsteps = conf.getStepsPerFrame()
		self.direction = Adafruit_MotorHAT.BACKWARD
		self.style = Adafruit_MotorHAT.DOUBLE

	#recommended for auto-disabling motors on shutdown!
	def turnOffMotors(self):
		self.mh.getMotor(1).run(Adafruit_MotorHAT.BRAKE)
		self.mh.getMotor(2).run(Adafruit_MotorHAT.BRAKE)
		self.mh.getMotor(3).run(Adafruit_MotorHAT.BRAKE)
		self.mh.getMotor(4).run(Adafruit_MotorHAT.BRAKE)
	
	def moveDolly(self):
		# Move dolly
		self.myStepper1.step(self.numsteps, self.direction, self.style)
		self.stepcount = self.stepcount+self.numsteps

	def getPosition(self):
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return float(self.stepcount)*float(pitch*teeth)/float(self.stepsPerRev)

	def getAngle(self):
		steps = self.config.getAngularStepsPerTeeth()
		teeth = self.config.getAngularTeeth()
		return float(self.anglecount)*float(360.0/(teeth*steps))

	def linearHome(self):
		if (self.direction == Adafruit_MotorHAT.BACKWARD):
			self.myStepper1.step(self.stepcount, Adafruit_MotorHAT.FORWARD, self.style)
		else:
			self.myStepper1.step(self.stepcount, Adafruit_MotorHAT.BACKWARD, self.style)
		self.stepcount = 0
		self.running = 0

	def anglularHome(self):
		if (self.direction == Adafruit_MotorHAT.BACKWARD):
			self.myStepper1.step(self.stepcount, Adafruit_MotorHAT.FORWARD, self.style)
		else:
			self.myStepper1.step(self.stepcount, Adafruit_MotorHAT.BACKWARD, self.style)
		self.stepcount = 0
		self.running = 0

	def isRunning(self):
		return self.running

	def start(self):
		self.running = 1

	def stop(self):
		self.running = 0
