import time
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
	
	def setMessageBroker(self,messagebroker):
		self.mBroker = messagebroker
	
	def worker(self):

	def getHeading(self):
		accel, mag = self.lsm303.read()
		accel_x, accel_y, accel_z = accel
		mag_x, mag_y, mag_z = mag
		print('Accel X={0}, Accel Y={1}, Accel Z={2}, Mag X={3}, Mag Y={4}, Mag Z={5}'.format(accel_x, accel_y, accel_z, mag_x, mag_y, mag_z))
		compassHeadin = 0
		if (mag_x != 0):
			compassHeadin = math.atan(mag_y/mag_x)
		return compassHeadin

	def getTilt(self):
		accel, mag = self.lsm303.read()
		accel_x, accel_y, accel_z = accel
		mag_x, mag_y, mag_z = mag
		print('Accel X={0}, Accel Y={1}, Accel Z={2}, Mag X={3}, Mag Y={4}, Mag Z={5}'.format(accel_x, accel_y, accel_z, mag_x, mag_y, mag_z))
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
