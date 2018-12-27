import json
import paho.mqtt.client as mqtt
from Camera import *


def on_log(client, userdata, level, buf):
	print("log: ",buf)

def on_message(client, userdata, message):
	msg =str(message.payload.decode("utf-8"))
	print("message received " ,msg)
	print("message topic=",message.topic)
	print("message qos=",message.qos)
	print("message retain flag=",message.retain)
#	if (msg == "start"):
#		self.camera.running = 1

class MessageBroker:
	mqtturl = "null"
	uname = "name"
	passwd = "passwd"
	type = "MQTT"
	
	def __init__(self, url, username, password,camera):
		# connec to server REST interface
		self.mqtturl=url
		self.uname=username
		self.passwd=password
		self.camera = camera
		self.client=mqtt.Client("CameraDolly")
		self.client.on_message=on_message
		self.client.on_log=on_log
		print("DataTransmitter.Init ready")
		#def __del__(self):
		#self.client.loop_stop()

	def on_message(client, userdata, message):
		msg =str(message.payload.decode("utf-8"))
		print("message received " ,msg)
		print("message topic=",message.topic)
		print("message qos=",message.qos)
		print("message retain flag=",message.retain)
		if (msg == "start"):
			self.camera.running = 1

	def connect(self):
		print("DataTransmitter.connect connecting to mqtt broker ", self.mqtturl)
		self.client.connect(self.mqtturl,port=1883)
		self.client.loop_start()
		self.client.subscribe("CameraDolly/ControlMessage/#")
		print("DataTransmitter.connect ready")
	
	def trasnmitdata(self,data,topic):
		print("DataTransmitter.trasnmitdata")
		
		datastr = str(data)
		datastr = datastr.replace("'","\"")
		self.client.publish(topic,payload=datastr,qos=0, retain=False)
#print("DataTransmitter.trasnmitdata ready")

