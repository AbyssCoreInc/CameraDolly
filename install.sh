#!/bin/sh

apt-get -y install gphoto2
apt-get -y install libgphoto2-dev
apt-get -y install mosquitto
apt-get -y install mosquitto-clients

pip3 install gphoto2
pip3 install paho-mqtt
pip3 install Adafruit_LSM303
pip3 install Adafruit_ADS1x15
pip3 install pytz

cp cameradolly.json /etc/
cp cameradolly.service /etc/systemd/system/
systemctl daemon-reload
systemctl start mosquitto
systemctl start cameradolly
