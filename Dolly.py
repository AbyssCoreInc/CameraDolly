import logging
import time
import math
from Configuration import *
from MessageBroker import *
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

class Dolly:
	LINEAR         = 0
	ANGULAR        = 1
	LINEARANGLULAR = 2
	LOCKLINEAR     = 3
	LOCKANGLULAR   = 4
	
	def __init__(self, configuration,motorhat):
		# create a default object, no changes to I2C address or frequency
		self.mh = motorhat
		self.config = configuration
		self.running = 0
		self.stepsPerRev = self.config.getStepsPerRev()
		self.myStepper1 = self.mh.getStepper(self.stepsPerRev, 1)      # 200 steps/rev, motor port #1
		self.myStepper1.setSpeed(self.config.getStepperSpeed())
		
		self.myStepper2 = self.mh.getStepper(self.stepsPerRev, 2)      # 200 steps/rev, motor port #1
		self.myStepper2.setSpeed(self.config.getStepperSpeed())
	
		self.xdist = 0
		self.ydist = 0
		self.mode  = Dolly.LINEAR
	
		self.stepcount = 0
		self.anglecount = 0
		self.numsteps = self.config.getStepsPerFrame()
		self.anglesteps = 0  # steps to rotate camera per frame (used in LocAngular and Anglular modes)
		self.direction = Adafruit_MotorHAT.BACKWARD
		self.style = Adafruit_MotorHAT.DOUBLE
	
		self.angleteeth = self.config.getAngularTeeth()
		self.anglestepsperteeth = self.config.getAngularStepsPerTeeth()

	#recommended for auto-disabling motors on shutdown!
	def turnOffMotors(self):
		self.mh.getMotor(1).run(Adafruit_MotorHAT.BRAKE)
		self.mh.getMotor(2).run(Adafruit_MotorHAT.BRAKE)
		self.mh.getMotor(3).run(Adafruit_MotorHAT.BRAKE)
		self.mh.getMotor(4).run(Adafruit_MotorHAT.BRAKE)
	
	def moveDolly(self):
		if (self.mode == Dolly.LINEAR):
			self.myStepper1.step(self.numsteps, self.direction, self.style)
			self.stepcount = self.stepcount+self.numsteps
				
		if (self.mode == Dolly.ANGULAR):
			self.rotateHead(self.anglesteps)
			self.anglecount = self.anglecount+self.anglesteps
		
		if (self.mode == Dolly.LINEARANGLULAR):
			self.rotateHead(self.anglesteps)
			self.anglecount = self.anglecount+self.anglesteps
			self.myStepper1.step(self.numsteps, self.direction, self.style)
			self.stepcount = self.stepcount+self.numsteps

		if (self.mode == Dolly.LOCKLINEAR):
			self.myStepper1.step(self.numsteps, self.direction, self.style)
			anglechange = self.calculateAngularSteps()
			self.rotateHead(anglechange)
			self.anglecount = self.anglecount+anglechange
			self.stepcount = self.stepcount+self.numsteps

		if (self.mode == Dolly.LOCKANGLULAR):
			stepstomove = self.calculateLinearSteps()
			self.myStepper1.step(stepstomove, self.direction, self.style)
			self.stepcount = self.stepcount+stepstomove
			
			self.rotateHead(self.anglesteps)
			self.anglecount = self.anglecount+self.anglesteps

	def rotateHead(self,steps):
			self.myStepper2.step(steps, self.direction, self.style)

	def calculateLinearSteps():
		if (self.mode == Dolly.LOCKANGLULAR):
			#determine X position
			x_comp = self.xdist-self.stepsToDistanceM(self.stepcount)
			y_comp = self.ydist
			alpha  = math.atan(x_comp/y_comp) # radians
			#delta is the angle in new position
			delta  = alhpa - self.angleStepsToRad(self.anglesteps)
			# determine how much x_component need to be moved
			return self.distanceToStepsM(math.tan(delta)*y_comp)
		else:
			return 0
				
	def calculateAngularSteps():
		if (self.mode == Dolly.LOCKLINEAR):
			# position where we start
			x_comp = self.xdist-self.stepsToDistanceM(self.stepcount)
			y_comp = self.ydist
			alpha  = math.atan(x_comp/y_comp) # radians of the fitst position
			#delta is the angle in new position
			x_delta = self.xdist-self.stepsToDistanceM(self.stepcount+self.numsteps)
			delta  = alhpa - math.atan(x_delta/y_comp)
			# determine how much x_component need to be moved
			return self.radiansToSteps(delta)
		else:
			return 0

	# retuns linear position of the dolly in millimeters
	def getPositionMM(self):
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return float(self.stepcount)*(float(pitch*teeth)/float(self.stepsPerRev))
	
	def getPositionM(self):
		return self.getPositionMM()/1000.0

	# retuns linear step size of the dolly in millimeters
	def getStepSizeMM(self):
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return float(self.numsteps)*float(pitch*teeth)/float(self.stepsPerRev)

	def getAngleDeg(self):
		steps = self.config.getAngularStepsPerTeeth()
		return float(self.anglecount)*float(360.0/(self.angleteeth*steps))

	def linearHome(self):
		if (self.direction == Adafruit_MotorHAT.BACKWARD):
			self.myStepper1.step(self.stepcount, Adafruit_MotorHAT.FORWARD, self.style)
		else:
			self.myStepper1.step(self.stepcount, Adafruit_MotorHAT.BACKWARD, self.style)
		self.stepcount = 0
		self.running = 0

	def setOperationModes(self,mode):
		if (self.running == 1):
			self.running = 0
			self.linearHome()
			self.anglularHome()
		
		self.mode = mode

	def getOperationMode(self):
		return self.mode

	# units meters
	def setTrackingX(self,xdist):
		self.xdist = xdist

	# units meters
	def setTrackingY(self,ydist):
		self.ydist = ydist

	# units meters
	def setStepDistance(self,dist):
		self.numsteps = self.distanceToStepsM(dist)
	
	# units meters
	def setStepAngle(self,angle):
		self.anglesteps = int(self.radiansToSteps(math.radians(angle)))
		print("setStepAngle "+str(angle)+" -> "+str(self.anglesteps))
	
	# Move andular axis to home and set counter to zero
	def anglularHome(self):
		if (self.direction == Adafruit_MotorHAT.BACKWARD):
			self.myStepper1.step(self.stepcount, Adafruit_MotorHAT.FORWARD, self.style)
		else:
			self.myStepper1.step(self.stepcount, Adafruit_MotorHAT.BACKWARD, self.style)
		self.anglestepcount = 0
		self.running = 0

	def isRunning(self):
		return self.running

	def start(self):
		self.running = 1

	def stop(self):
		self.running = 0
	
	def angleStepsToRad(self,steps):
		return steps * math.radians(360/(self.angleteeth*self.anglestepsperteeth))
	def radiansToSteps(self,rads):
		return rads/math.radians(360/(self.angleteeth*self.anglestepsperteeth))
	
	def stepsToDistanceM(self,steps):
		return (((self.teeth*self.pitch)/self.stepsPerRev)*steps)/1000
	
	def distanceToStepsM(self,dist):
		return (1000*dist)/(((self.teeth*self.pitch)/self.stepsPerRev))


