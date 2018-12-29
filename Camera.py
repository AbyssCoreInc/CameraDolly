import gphoto2 as gp
import logging
from Configuration import *

class Camera:
	cameramodel
	
	def __init__(self, configuration):
		self.config = configuration
		self.running = 0
		self.camearamodel = "nd"

	def initCamera(self):
		logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
	
		gp.check_result(gp.use_python_logging())
		context = gp.gp_context_new()
		self.camera = gp.check_result(gp.gp_camera_new())
		while True:
			try:
				gp.gp_camera_init(self.camera,context)
				#self.camera.init(context)
			except gp.GPhoto2Error as ex:
				if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
					# no camera, try again in 2 seconds
					time.sleep(2)
					continue
				# some other error we can't handle here
				raise
			# operation completed successfully so exit loop
			break
		#gp.check_result(gp.gp_camera_init(self.camera,context))
		camconfig = gp.check_result(gp.gp_camera_get_config(self.camera))
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

 		abilities = gp.check_result(gp.gp_camera_get_abilities(camera))
		this.cameramodel = abilities.model

	def setShutterSpeed(self,speed):
		return 0
	
	def takePicture(self):
		file_path = gp.check_result(gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE))
		print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))

	def __del__(self):
		gp.check_result(gp.gp_camera_exit(self.camera))

