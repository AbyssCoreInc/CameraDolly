
import time
from Configuration import *
from MessageBroker import *
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor


class LensHeater:
	def __init__(self, motorhat):
		self.pwmFreq = 10
		self.pwm = 50
		self.mh = motorhat
	
	def worker(self):
		counter = 0
		while True:
			time.sleep(1/self.pwmFreq)
			counter = counter+1
			if (counter < self.pwm)
				mh.setPin(0,1)
			else
				mh.setPin(0,0)
			if (counter > 100)
				counter = 0

	def setPWM(self,count):
		self.pwm = count

	def setPwmFreq(self,freq):
		self.pwmFreq = freq

	def getPWM(self):
		return self.pwm
	def getPwmFreq(self):
		return self.pwmFreq

