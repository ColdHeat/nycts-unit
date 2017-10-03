#!/bin/bash

cd /home/pi/nycts-unit
sudo python reset.py &
sudo python load.py &

cd /home/pi/nycts-unit/headless
sudo npm run start

cd /home/pi/nycts-unit/api
node bonjour.js &
node index.js &
pkill -f load.py
sleep 10
cd /home/pi/nycts-unit
sudo python start.py &
sudo python monitor.py &

while true; do
	sleep 60
	pkill -f bonjour.js
	sleep 1
	cd /home/pi/nycts-unit/api
	node bonjour.js &
done