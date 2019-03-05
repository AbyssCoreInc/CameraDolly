import logging
import time
import math
from Configuration import *
from MessageBroker import *
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_StepperMotor
import Adafruit_LSM303
import RPi.GPIO as GPIO


class Dolly:
	LINEAR         = 0
	ANGULAR        = 1
	LINEARANGLULAR = 2
	LOCKLINEAR     = 3
	LOCKANGLULAR   = 4
	
	
	def __init__(self, configuration,motorhat):
		# create a default object, no changes to I2C address or frequency
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(21, GPIO.FALLING, callback=self.startCallback, bouncetime=300)
		GPIO.add_event_detect(26, GPIO.FALLING, callback=self.endCallback, bouncetime=300)
		self.lsm303 = Adafruit_LSM303.LSM303()
		
		self.mh = motorhat
		self.config = configuration
		self.running = 0
		self.stepsPerRev = self.config.getStepsPerRev()
		self.myStepper1 = self.mh.getStepper(self.stepsPerRev, 1)      # 200 steps/rev, motor port #1
		self.myStepper1.setSpeed(self.config.getStepperSpeed())
		
		self.myStepper2 = self.mh.getStepper(self.stepsPerRev, 2)      # 200 steps/rev, motor port #1
		self.myStepper2.setSpeed(self.config.getStepperSpeed())
	
		self.interval = self.config.getDefInterval()
		
		self.xdist = 0
		self.ydist = 0
		self.mode  = Dolly.LINEAR
		
		self.atTheEnd = 0
		self.atTheStart = 0
		
		self.pitch = self.config.getLinearPitch()
		self.teeth = self.config.getLinearTeeth()
		
		self.declination = 0.0
	
		self.stepcount = 0
		self.anglecount = 0
		self.numsteps = self.config.getStepsPerFrame()
		self.anglesteps = 0  # steps to rotate camera per frame (used in LocAngular and Anglular modes)
		self.direction = Adafruit_MotorHAT.BACKWARD
		self.style = Adafruit_MotorHAT.DOUBLE
	
		self.angleteeth = self.config.getAngularTeeth()
		self.anglestepsperteeth = self.config.getAngularStepsPerTeeth()
	
	
	def startCallback(self,channel):
		print("falling edge detected on 21")
		self.atTheStart = 1
		self.atTheEnd = 0

	def endCallback(self,channel):
		print("falling edge detected on 26")
		self.atTheStart = 0
		self.atTheEnd = 1
	
	#recommended for auto-disabling motors on shutdown!
	def turnOffMotors(self):
		self.mh.getMotor(1).run(Adafruit_MotorHAT.BRAKE)
		self.mh.getMotor(2).run(Adafruit_MotorHAT.BRAKE)
		self.mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
		self.mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
	
	def moveDolly(self):
		if (self.mode == Dolly.LINEAR):
			self.stepDolly(self.numsteps)
			self.stepcount = self.stepcount+self.numsteps
				
		if (self.mode == Dolly.ANGULAR):
			print("self.mode == Dolly.ANGULAR")
			self.rotateHead(self.anglesteps)
			self.anglecount = self.anglecount+self.anglesteps
		
		if (self.mode == Dolly.LINEARANGLULAR):
			print("self.mode == Dolly.LINEARANGLULAR")
			self.rotateHead(self.anglesteps)
			self.anglecount = self.anglecount+self.anglesteps
			self.stepDolly(self.numsteps)
			self.stepcount = self.stepcount+self.numsteps

		if (self.mode == Dolly.LOCKLINEAR):
			print("self.mode == Dolly.LOCKLINEAR")
			self.stepDolly(self.numsteps)
			anglechange = self.calculateAngularSteps()
			self.rotateHead(anglechange)
			self.anglecount = self.anglecount+anglechange
			self.stepcount = self.stepcount+self.numsteps

		if (self.mode == Dolly.LOCKANGLULAR):
			print("self.mode == Dolly.LOCKANGLULAR")
			stepstomove = self.calculateLinearSteps()
			
			self.stepDolly(stepstomove)
			self.stepcount = self.stepcount+stepstomove
			
			self.rotateHead(self.anglesteps)
			self.anglecount = self.anglecount+self.anglesteps

	def stepDolly(self,steps):
		if (self.direction == Adafruit_MotorHAT.FORWARD and self.atTheEnd == 0):
			self.myStepper1.step(steps, self.direction, self.style)
			#check if GPIO is cleared and clear the flag
			if(GPIO.input(21) is False):
				self.atTheStart = 0
		if (self.direction == Adafruit_MotorHAT.BACKWARD and self.atTheStart == 0):
			self.myStepper1.step(steps, self.direction, self.style)
			#check if GPIO is cleared and clear the flag
			if(GPIO.input(26) is False):
				self.atTheEnd = 0
	
	
	def rotateHead(self,steps):
		print("rotateHead"+str(steps))
		self.myStepper2.step(steps, self.direction, self.style)
        self.myStepper2.
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
		result = float(self.stepcount)*(float(pitch*teeth)/float(self.stepsPerRev))
		print("Dolly.getPositionMM = "+str(result))
		return result
	
	def setDeclination(self,dec):
		self.declination = dec
	
	def getPositionM(self):
		return self.getPositionMM()/1000.0

	# retuns linear step size of the dolly in millimeters
	def getStepSizeMM(self):
		#print("Dolly.getPositionMM "+str(self.pitch)+" x "+str(self.teeth) + " x " + str(self.stepsPerRev))
		ditance = (self.numsteps*self.pitch*self.teeth)/self.stepsPerRev
		#print("Dolly.getStepSizeMM = " + str(ditance))
		return ditance
	
	def getAngleDeg(self):
		steps = self.config.getAngularStepsPerTeeth()
		return float(self.anglecount)*float(360.0/(self.angleteeth*steps))

	def linearHome(self):
		self.stepDolly(self.stepcount)
		#move dolly until oneof the interrupts fires
		while(self.atTheStart == 0):
			self.stepDolly(self.numsteps)
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
	
	def getTrackingY(self):
		return self.ydist
	
	def getTrackingX(self):
		return self.xdist

	# units meters
	def setStepDistance(self,dist):
		self.numsteps = self.distanceToStepsMM(dist)
	
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
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return (((teeth*pitch)/self.stepsPerRev)*steps)/1000
	
	def stepsToDistanceMM(self,steps):
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return (((teeth*pitch)/self.stepsPerRev)*steps)
	
	def distanceToStepsM(self,dist):
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return int((1000*dist)/(((teeth*pitch)/self.stepsPerRev)))

	def distanceToStepsMM(self,dist):
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return int((dist)/(((teeth*pitch)/self.stepsPerRev)))
	def getHeadAlignment(self):
		accel, mag = self.lsm303.read()
		accel_x, accel_y, accel_z = accel
		mag_x, mag_y, mag_z = mag
		print('Accel X={0}, Accel Y={1}, Accel Z={2}, Mag X={3}, Mag Y={4}, Mag Z={5}'.format(accel_x, accel_y, accel_z, mag_x, mag_y, mag_z))
	def getHeading(self):
		accel, mag = self.lsm303.read()
		accel_x, accel_y, accel_z = accel
		mag_x, mag_y, mag_z = mag
		print('Accel X={0}, Accel Y={1}, Accel Z={2}, Mag X={3}, Mag Y={4}, Mag Z={5}'.format(accel_x, accel_y, accel_z, mag_x, mag_y, mag_z))
		compassHeadin = math.atan(mag_y/mag_x)
		return compassHeadin

	def getTilt(self):
		accel, mag = self.lsm303.read()
		accel_x, accel_y, accel_z = accel
		mag_x, mag_y, mag_z = mag
		print('Accel X={0}, Accel Y={1}, Accel Z={2}, Mag X={3}, Mag Y={4}, Mag Z={5}'.format(accel_x, accel_y, accel_z, mag_x, mag_y, mag_z))
		tilt = math.atan(accel_x/accel_z)
		return tilt
	def setInterval(self,inter):
		self.interval = inter
	def getInterval(self):
		return self.interval

    def gotoStart(self):
        self.stop()
        self.seekHome()

        
