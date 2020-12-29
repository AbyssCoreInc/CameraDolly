#!/bin/sh

apt-get -y install gphoto2
apt-get -y install libgphoto2-dev


pip3 install gphoto2
pip3 install paho-mqtt
pip3 install Adafruit_LSM303
pip3 install Adafruit_ADS1x15
pip3 install pytz

cp cameradolly.json /etc/
