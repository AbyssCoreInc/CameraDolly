import time
import math
from Configuration import *
from MessageBroker import *
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from LIS3DH import LIS3DH

class CameraHead:
	def __init__(self, motorhat,config):
		self.mh = Adafruit_MotorHAT(i2c_bus=0)
		self.IMU = LIS3DH(debug=True)
		self.IMU.setRange(LIS3DH.RANGE_2G)
		self.mh = motorhat
		self.tiltMotor = self.mh.getMotor(1)      # Head Tilt motor
		self.tiltMotor.setSpeed(255)
		self.rotateMotor = self.mh.getMotor(4)      #  Head Motor on channel 4
		self.rotateMotor.setSpeed(255)
		#self.levelMargin = 0.0174533 # 1° in radians
		self.levelMargin = 0.00436333 # 0.5° in radians
		self.alignMargin = 0.00872665 # 0.5°
	
	def setMessageBroker(self,messagebroker):
		self.mBroker = messagebroker
	
	#	def worker(self):

	def getHeading(self):
		#accel, mag = self.lsm303.read()
		#accel_x, accel_y, accel_z = accel
		#mag_x, mag_y, mag_z = mag
		#print('Accel X={0}, Accel Y={1}, Accel Z={2}, Mag X={3}, Mag Y={4}, Mag Z={5}'.format(accel_x, accel_y, accel_z, mag_x, mag_y, mag_z))
		#compassHeadin = 0
		#if (mag_x != 0):
		#	compassHeadin = math.atan(mag_y/mag_x)
		#return compassHeadin
		return 0 # Got only accelerometer...
	
	def getTilt(self):
		#accel, mag = self.lsm303.read()
		#accel_x, accel_y, accel_z = accel
		#mag_x, mag_y, mag_z = mag
		#print('Accel X={0}, Accel Y={1}, Accel Z={2}, Mag X={3}, Mag Y={4}, Mag Z={5}'.format(accel_x, accel_y, accel_z, mag_x, mag_y, mag_z))
		accel_x = self.IMU.getX()
		accel_z = self.IMU.getZ()
		tilt = 0
		if (accel_z != 0):
			tilt = math.atan(accel_x/accel_z)
		return tilt

	def setDeclination(self,dec):
		self.declination = dec

	def rotateHead(self,speed=255,dir=Adafruit_MotorHAT.FORWARD):
		print("rotateHead"+str(speed))
		self.rotateMotor.setSpeed(speed)
		self.rotateMotor.run(dir)
	
	def tiltHead(self,speed=255,dir=Adafruit_MotorHAT.FORWARD,delay=0.1):
		print("rotateHead"+str(speed))
		self.tiltMotor.setSpeed(speed)
		self.tiltMotor.run(dir)
		time.sleep(delay)
		self.tiltMotor.run(Adafruit_MotorHAT.RELEASE)
		time.sleep(delay*5)

	def rotateCW(self):
		self.rotateMotor.run(Adafruit_MotorHAT.FORWARD)
		time.sleep(self.rotateTick)
		self.rotateMotor.run(Adafruit_MotorHAT.RELEASE)
						 
	def rotateCCW(self):
		self.rotateMotor.run(Adafruit_MotorHAT.BACKWARD)
		time.sleep(self.rotateTick)
		self.rotateMotor.run(Adafruit_MotorHAT.RELEASE)
						 
	def headOff(self):
		self.rotateMotor.run(Adafruit_MotorHAT.RELEASE)
		self.rotateMotor.run(Adafruit_MotorHAT.RELEASE)

	def levelHeadHorizon(self):
		tilt = self.getTilt()
		while(math.fabs(tilt) > self.levelMargin):
			print("levelHeadHorizon: "+str(math.fabs(tilt))+" margin: "+str(self.levelMargin))
			if (tilt < 0):
				self.tiltHead(dir=Adafruit_MotorHAT.FORWARD)
			else:
				self.tiltHead(dir=Adafruit_MotorHAT.BACKWARD)
			tilt = self.getTilt()
		print("Horizon leveled")
				
	def alignEarthAxis(self,latitude): # radians
		tilt = self.getTilt()
		#targetAngle = 1.5708 - float(latitude)
		targetAngle = float(latitude)
		
		while(math.fabs(tilt-targetAngle) > self.alignMargin):
			print("alignEarthAxis: delta "+str(math.fabs(targetAngle-tilt))+" tilt: "+str(tilt)+" target: "+str(targetAngle))
			if (tilt < targetAngle):
				self.tiltHead(dir=Adafruit_MotorHAT.FORWARD)
			else:
				self.tiltHead(dir=Adafruit_MotorHAT.BACKWARD)
			tilt = self.getTilt()
		print("Axis aligned")
