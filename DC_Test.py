import sys
import time
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor


class Tester:
	def __init__(self):
		# create a default object, no changes to I2C address or frequency
		self.mh = Adafruit_MotorHAT(i2c_bus=0)
		self.myMotor1 = self.mh.getMotor(1)      # Head Tilt motor
		self.myMotor1.setSpeed(255)

		self.myMotor2 = self.mh.getMotor(2)      # Linear movement motor
		self.myMotor2.setSpeed(255)

		self.myMotor3 = self.mh.getMotor(4)      #  Head Motor on channel 4
		self.myMotor3.setSpeed(255)

		i2c = busio.I2C(board.SCL, board.SDA)
		self.adc = ADS.ADS1115(i2c)
		self.GAIN = 1
		self.AMP = 25
#		self.adc.gain = self.GAIN


	def go(self,direction):
#		self.myMotor1.run(direction)
#		self.myMotor2.run(direction)
		self.myMotor3.run(direction)


	def stop(self):
		self.myMotor1.run(Adafruit_MotorHAT.RELEASE)
		self.myMotor2.run(Adafruit_MotorHAT.RELEASE)

tester = Tester()

interator = 10
tester.go(Adafruit_MotorHAT.FORWARD)
#tester.go(Adafruit_MotorHAT.BACKWARD)
while (iterator > 0):
	time.sleep(0.5)
	iterator = iterator - 1
#	print("1: "+str(self.chanS1)+" 2: "+str(self.chanS2)+" 3: "+str(self.chanS3)+" 4: "+str(self.chanS4))
tester.stop()

