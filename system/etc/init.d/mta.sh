#!/bin/bash

cd /home/pi/nycts-unit
sudo python reset.py &
sudo python load.py &

cd /home/pi/nycts-unit/headless
sudo npm run start

cd /home/pi/nycts-unit/api
node index.js &
sleep 10
pkill -f load.py
pkill -f readytopair.py

sleep 10

cd /home/pi/nycts-unit/
sudo python jobs.py

cd /home/pi/nycts-unit
sudo python start.py &
sudo python monitor.py
