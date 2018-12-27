import gphoto2 as gp

class Camera:
	def __init__(self, configuration):
		self.config = configuration
		self.running = 0

	def initCamera():
		logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
	
		gp.check_result(gp.use_python_logging())
		context = gp.gp_context_new()
		self.camera = gp.check_result(gp.gp_camera_new())
		gp.check_result(gp.gp_camera_init(self.camera,context))
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

	def setShutterSpeed(speed):
		return 0
	
	def takePicture():
		print('Capturing image: '+str(counter))
		file_path = gp.check_result(gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE))
		print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))

	def __del__(self):
		gp.check_result(gp.gp_camera_exit(self.camera))

