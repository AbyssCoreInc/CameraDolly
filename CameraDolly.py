from __future__ import print_function

import logging
import os
import subprocess
import sys
import gphoto2 as gp
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import time
import atexit
import threading
import random

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT()

# create empty threads (these will hold the stepper 1 and 2 threads)
st1 = threading.Thread()

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.BRAKE)
    mh.getMotor(2).run(Adafruit_MotorHAT.BRAKE)
    mh.getMotor(3).run(Adafruit_MotorHAT.BRAKE)
    mh.getMotor(4).run(Adafruit_MotorHAT.BRAKE)

atexit.register(turnOffMotors)
myStepper1 = mh.getStepper(200, 1)      # 200 steps/rev, motor port #1
myStepper1.setSpeed(60)          # 30 RPM

numsteps = 9
direction = Adafruit_MotorHAT.BACKWARD
style = Adafruit_MotorHAT.DOUBLE

def main():
    logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    context = gp.gp_context_new()
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera,context))

    images = 1440
    counter = 0

    config = gp.check_result(gp.gp_camera_get_config(camera))
    # find the capture target config item
    capture_target = gp.check_result(
        gp.gp_widget_get_child_by_name(config, 'capturetarget'))
    # print current setting
    value = gp.check_result(gp.gp_widget_get_value(capture_target))
    print('Current setting:', value)
    # print possible settings
    for n in range(gp.check_result(gp.gp_widget_count_choices(capture_target))):
        choice = gp.check_result(gp.gp_widget_get_choice(capture_target, n))
        print('Choice:', n, choice)

    gp.check_result(gp.gp_widget_set_value(capture_target, "Memory card"))
    gp.check_result(gp.gp_camera_set_config(camera, config, context))

    while (counter < images):
        counter = counter + 1
        # Move dolly
        myStepper1.step(numsteps, direction, style)
	# Wait for awhile
        time.sleep(1)
        # Capture image
        print('Capturing image: '+str(counter))
        file_path = gp.check_result(gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE))
        print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))

    gp.check_result(gp.gp_camera_exit(camera))
    return 0

if __name__ == "__main__":
    sys.exit(main())
