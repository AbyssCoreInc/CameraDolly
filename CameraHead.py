import time
from Configuration import *
from MessageBroker import *
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import Adafruit_LSM303

class LensHeater:
	def __init__(self, motorhat,config):
		self.mh = Adafruit_MotorHAT(i2c_bus=0)
		self.lsm303 = Adafruit_LSM303.LSM303()
	
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

	def rotateHead(self,steps):
		print("rotateHead"+str(steps))
		self.head.rotate(
		count = 0
		if (steps < 0):
			dir = STEPPER.FORWARD
			steps = steps * -1
		else:
			dir = STEPPER.BACKWARD
		while (count < steps):
			self.myStepper2.onestep(direction=dir, style=self.style)
			count = count + 1
			self.myStepper2.release()
