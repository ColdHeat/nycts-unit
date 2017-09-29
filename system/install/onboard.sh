#!/bin/bash

# Install NYC Train Sign Unit Firmware
cd /home/pi
sudo git clone https://github.com/nyc-train-sign/nycts-unit

# Install necessary packages for Python
cd /home/pi/nycts-unit/system/install
sudo easy_install pip &
sudo pip install -r requirements.txt

# Install necessary packages for Node
cd /home/pi/nycts-unit/api
sudo yarn install

# Install necessary packages for Bonjour
cd /home/pi/nycts-unit/headless
sudo npm install
