import gphoto2 as gp
import logging
import time
from Configuration import *
from MessageBroker import *

class Camera:
	cameramodel = "unknown"
	
	def __init__(self, configuration):
		self.config = configuration
		self.running = 0
		self.cameramodel = "unknown"
		self.images = 1000

	def setMessageBroker(self,messagebroker):
		self.mBroker = messagebroker

	def initCamera(self):
		#logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
	
		gp.check_result(gp.use_python_logging())
		context = gp.gp_context_new()
		self.camera = gp.check_result(gp.gp_camera_new())
		while True:
			try:
				gp.gp_camera_init(self.camera,context)
				#self.camera.init(context)
				camconfig = gp.check_result(gp.gp_camera_get_config(self.camera))
			except gp.GPhoto2Error as ex:
				print("BUIUYAAH")
				# no camera, try again in 2 seconds
				time.sleep(2)
				continue
			# operation completed successfully so exit loop
			break
		#gp.check_result(gp.gp_camera_init(self.camera,context))
		#camconfig = gp.check_result(gp.gp_camera_get_config(self.camera))
		# find the capture target config item
		capture_target = gp.check_result(gp.gp_widget_get_child_by_name(camconfig, 'capturetarget'))
		# print current setting
		value = gp.check_result(gp.gp_widget_get_value(capture_target))
		print('Current setting:', value)
		# print possible settings
		for n in range(gp.check_result(gp.gp_widget_count_choices(capture_target))):
			choice = gp.check_result(gp.gp_widget_get_choice(capture_target, n))
			print('Choice:', n, choice)

		gp.check_result(gp.gp_widget_set_value(capture_target, "Memory card"))
		gp.check_result(gp.gp_camera_set_config(self.camera, camconfig, context))

		abilities = gp.check_result(gp.gp_camera_get_abilities(self.camera))
		self.cameramodel = abilities.model
		
		# try to read shutter speeds
		text = gp.gp_camera_get_summary(self.camera)
		print(text[0].text)
		

	def setShutterSpeed(self,speed):
		return 0

	def takePicture(self):
		if (self.config.isSimulation() == 0):
			file_path = gp.check_result(gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE))
			print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
		else:
			print("Camera.takePicture() simulated")

	def setImageNumber(self, images):
		self.images = images

	def getImageNumber(self):
		print("Camera.getImageNumber "+str(self.images))
		return self.images

	def __del__(self):
		gp.check_result(gp.gp_camera_exit(self.camera))

	def getCameraModel(self):
		if (self.config.isSimulation() == 0):
			return self.cameramodel
		else:
			return "Simulation"
	
	def sendModel(self):
		self.mBroker.trasnmitdata("cammodel"+self.cameramodel, self.config.getTopic()+"StatusMessage")
