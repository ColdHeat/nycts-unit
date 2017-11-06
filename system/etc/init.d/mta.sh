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

cd /home/pi/nycts-unit/system/watchdog
sudo python jobs.py

cd /home/pi/nycts-unit
sudo python start.py &
sudo python monitor.py

sleep 10
sudo python /home/pi/nycts-unit/system/watchdog/spy.py
