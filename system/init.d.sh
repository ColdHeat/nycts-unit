#!/bin/bash

cd /home/pi/nycts-unit
sudo python load.py &

STATE="loading";

while [ $STATE == "loading" ]
do
    #do a ping and check that its not a default message or change to grep for something else
    STATE=$(ping -q -W 1 -c 1 google.com > /dev/null && echo ok || echo loading)

    #sleep for 1 seconds and try again
    sleep 5

done

GIT_STATE=$(su pi --preserve-environment -c "cd /home/pi/nycts-unit && git pull" > "Already up to date." &&  echo ok || echo bad)
if [ $GIT_STATE == "bad" ]; then
  yarn install
fi
cd /home/pi/nycts-unit/api
pkill -f load.py
node index.js &
sleep 10
cd /home/pi/nycts-unit
sudo python start.py
#sudo python combo.p