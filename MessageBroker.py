import json
import paho.mqtt.client as mqtt
from uuid import getnode as get_mac
from Camera import *
import CameraDolly
from Configuration import *
import time
import datetime
from datetime import datetime, date, timedelta
from pytz import timezone

def on_log(client, userdata, level, buf):
	print("log: ",buf)

class MessageBroker:
	mqtturl = "null"
	uname = "name"
	passwd = "passwd"
	type = "MQTT"
	
	def __init__(self, conf,camera,dolly,heater):
		# connec to server REST interface
		self.conf = conf
		self.mqtturl=conf.getMQTTURL()
		self.uname=conf.getMqttUsername()
		self.passwd=conf.getMqttPassword()
		self.camera = camera
		self.heater = heater
		self.dolly = dolly
		self.client=mqtt.Client("CameraDolly")
		self.client.on_message=self.on_message
		self.client.on_log=on_log
		print("DataTransmitter.Init ready")
		#def __del__(self):
		#self.client.loop_stop()

	# Handle incoming MQTT messages. Parses control messages. Message format is "[commang]-[value]"
	# at this point it is verstile enough. If more sophistication like timestamps, etc are needed
	# better messaging has be implemented. To other direction message tries to be NGSI compliatn JSON so
	# similar approach could be used.
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
			self.transmitCameraModel()
		if (msg == "getstepsize"):
			self.sendStepSize()
		if (msg == "getstepcount"):
			sendStepCount()
		if (msg == "getmode"):
			sendOpMode()
		if (msg == "gettracking"):
			sendTracking()
		if (msg == "getposition"):
			self.transmitPositionMessage(dolly.getPositionMM, dolly.getAngleDeg(), getCounter())
		if (msg == "getheatsetting"):
			self.heater.sendHeatSetting()
		if (msg == "setheat"):
			print("on_message: set heat to "+setting)
			self.heater.setPWM(int(setting))
		if (msg == "setmode"):
			print("on_message: set mode to "+setting)
			self.dolly.setOperationModes(int(setting))
		if (msg == "settargetx"):
			print("on_message: set tracking X to "+setting)
			self.dolly.setTrackingX(int(setting))
		if (msg == "settargety"):
			print("on_message: set tracking Y to "+setting)
			self.dolly.setTrackingY(int(setting))
		if (msg == "setstepdistance"):
			print("on_message: set step distance to "+setting)
			self.dolly.setStepDistance(int(setting))
		if (msg == "setanglestep"):
			print("on_message: set angle step to "+setting)
				self.dolly.setStepAngle(float(setting))
			
	def connect(self):
		print("DataTransmitter.connect connecting to mqtt broker ", self.mqtturl)
		self.client.connect(self.mqtturl,port=1883)
		print("DataTransmitter.connect ready")
	
	def getTimeStamp(self):
		ts = time.time()
		utcts = datetime.utcfromtimestamp(ts)
		zonets = timezone('UTC').localize(utcts)
		timestamp = zonets.strftime('%Y-%m-%dT%H:%M:%S')
		return timestamp
	
	# Method to construct ID field for NGSI service desciption messages (not used right now)
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

	# Method for contructing ID field for dolly NGSI status messages
	def getDollyIDField(self):
		mac = get_mac()
		field = ""
		field = field + "\t\"id\":\""+str(mac)+"\",\n"
		field = field + "\t\"type\":\"dolly\",\n"
		field = field + "\t\"isPattern\":\"false\",\n"
		return field
	
	# Method for transmitting dolly position status message
	# Sends position on rail, angle of the camera head and number of images taken
	def transmitPositionMessage(self, position, angle, images):
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
		message = message + "}"
		self.transmitdata(message,self.conf.getTopic()+"PositionMessage")

	# Method for transmitting camera model string
	# Sends camera model to subsribers
	def transmitCameraModel(self):
		mac = get_mac()
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"cameramodel\",\n"
		message = message + "\t\t\t\"type\":\"string\",\n"
		message = message + "\t\t\t\"value\":\""+self.camera.getCameraModel()+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "}"
		self.transmitdata(message,self.conf.getTopic()+"CameraModelMessage")
	
	def sendStepSize():
		mac = get_mac()
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"stepsize\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getStepSizeMM())+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"anglestep\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getAngleDeg())+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "}"
		self.transmitdata(message,self.conf.getTopic()+"PositionMessage")
	
	def sendOpMode():
		mac = get_mac()
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"operationmode\",\n"
		message = message + "\t\t\t\"type\":\"integer\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getOperationMode())+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "}"
		self.transmitdata(message,self.conf.getTopic()+"PositionMessage")

	def sendTracking():
		mac = get_mac()
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"trackx\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getStepSizeMM())+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"tracky\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getAngleDeg())+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "}"
		self.transmitdata(message,self.conf.getTopic()+"PositionMessage")

	def transmitdata(self,data,topic):
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

