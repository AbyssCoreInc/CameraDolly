import json
import paho.mqtt.client as mqtt
from Camera import *
import CameraDolly
import time


def on_log(client, userdata, level, buf):
	print("log: ",buf)

class MessageBroker:
	mqtturl = "null"
	uname = "name"
	passwd = "passwd"
	type = "MQTT"
	
	def __init__(self, url, username, password,camera,heater):
		# connec to server REST interface
		self.mqtturl=url
		self.uname=username
		self.passwd=password
		self.camera = camera
		self.heater = heater
		self.client=mqtt.Client("CameraDolly")
		self.client.on_message=self.on_message
		self.client.on_log=on_log
		print("DataTransmitter.Init ready")
		#def __del__(self):
		#self.client.loop_stop()

	def on_message(self,client, userdata, message):
		msge =str(message.payload.decode("utf-8"))
		print("message received " ,msge)
		print("message topic=",message.topic)
		print("message qos=",message.qos)
		print("message retain flag=",message.retain)
		if (len(msge.split("-")) != 2):
			msg = msge
		else:
			msg,setting = msge.split("-")
		
		if (msg == "start"):
			self.camera.running = 1
		if (msg == "stop"):
			self.camera.running = 0
		if (msg == "cammodel"):
			self.camera.sendModel()
		if (msg == "getstepsize"):
			sendStepSize()
		if (msg == "getstepcount"):
			sendStepCount()
		if (msg == "getheatsetting"):
			self.heater.sendHeatSetting()
		if (msg == "setheat"):
			print("on_message: set heat to "+setting)
			self.heater.setPWM(int(setting))
			
	def connect(self):
		print("DataTransmitter.connect connecting to mqtt broker ", self.mqtturl)
		self.client.connect(self.mqtturl,port=1883)
		
		print("DataTransmitter.connect ready")
	
	def trasnmitdata(self,data,topic):
		print("DataTransmitter.trasnmitdata topic:"+topic+" msg:"+data)
		
		datastr = str(data)
		datastr = datastr.replace("'","\"")
		self.client.publish(topic,payload=datastr,qos=0, retain=False)

	def worker(self):
		self.client.subscribe("CameraDolly/ControlMessage")
		self.client.loop_start()
		try:
			while True:
				time.sleep(1)
				print("Wait messages")
		except KeyboardInterrupt:
			print("exiting")
		self.client.disconnect()
		self.client.loop_stop()
#print("DataTransmitter.trasnmitdata ready")

