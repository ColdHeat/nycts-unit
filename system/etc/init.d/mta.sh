#!/bin/bash

cd /home/pi/nycts-unit
sudo python reset.py &
sudo python load.py &

cd /home/pi/nycts-unit/headless
sudo npm run start

cd /home/pi/nycts-unit/api
node index.js &
sleep 5
pkill -f load.py
pkill -f readytopair.py &
sudo python /home/pi/nycts-unit/settingupsign.py &

sleep 5

cd /home/pi/nycts-unit/system/watchdog
sudo python jobs.py &
sudo python spy.py

cd /home/pi/nycts-unit
pkill -f settingupsign.py &
sudo python start.py &
sudo python monitor.py
