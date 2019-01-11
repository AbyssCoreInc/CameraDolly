import json
import paho.mqtt.client as mqtt
from uuid import getnode as get_mac
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
	
	def __init__(self, url, username, password,camera,dolly,heater):
		# connec to server REST interface
		self.mqtturl=url
		self.uname=username
		self.passwd=password
		self.camera = camera
		self.heater = heater
		self.dolly = dolly
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
			self.dolly.start()
		if (msg == "stop"):
			self.dolly.stop()
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
	
	def getTimeStamp(self):
		ts = time.time()
		utcts = datetime.datetime.utcfromtimestamp(ts)
		zonets = timezone('UTC').localize(utcts)
		timestamp = zonets.strftime('%Y-%m-%dT%H:%M:%S')
		return timestamp
	
	def getDollyIDServiceField(self):
		mac = get_mac()
		#field = "{\n"
		field = ""
		field = field + "\"_id\":{\n"
		field = field + "\t\t\"id\":\""+mac+"\",\n"
		field = field + "\t\t\"type\":\"dolly\",\n"
		field = field + "\t\t\"servicePath\":\"/dolly\",\n"
		field = field + "}"
		return field
	def getDollyIDField(self):
		mac = get_mac()
		field = ""
		field = field + "\t\"id\":\""+mac+"\",\n"
		field = field + "\t\"type\":\"dolly\",\n"
		field = field + "\t\"isPattern\":\"false\",\n"
		return field
	
	def transmitPositionMessage(position, angle, images):
		mac = get_mac()
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"position\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(position)+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"angle\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(angle)+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"images\",\n"
		message = message + "\t\t\t\"type\":\"integer\",\n"
		message = message + "\t\t\t\"value\":\""+str(images)+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = "}"
		self.transmitdata(message,conf.getTopic()+"PositionMessage")
	

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

