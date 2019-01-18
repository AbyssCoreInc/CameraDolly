import sys
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_StepperMotor


class Tester:
	def __init__(self):
		# create a default object, no changes to I2C address or frequency
		self.mh = Adafruit_MotorHAT()
		self.myStepper1 = self.mh.getStepper(200, 1)      # 200 steps/rev, motor port #1
		self.myStepper1.setSpeed(60)
		
		self.myStepper2 = self.mh.getStepper(200, 2)      # 200 steps/rev, motor port #1
		self.myStepper2.setSpeed(60)
		
		self.style = Adafruit_MotorHAT.DOUBLE
		
	def step(self,direction,steps):
		self.myStepper1.step(steps, direction, self.style)
		self.myStepper2.step(steps, direction, self.style)


tester = Tester()

while(1):
	tester.step(int(sys.argv[1]),int(sys.argv[2]))


