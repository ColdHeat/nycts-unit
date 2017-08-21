#!/bin/bash

cd /home/pi/nycts-unit
sudo python load.py &

STATE="loading";
i=0;
offline=false;
while [ $STATE == "loading" ]
do
	i++
    #do a ping and check that its not a default message or change to grep for something else
    STATE=$(ping -q -W 1 -c 1 google.com > /dev/null && echo ok || echo loading)

    #sleep for 1 seconds and try again
    sleep 5

    if [ $i == 10 ]; then
  		offline=true
	fi
done

if [ offline == false ]; then
	GIT_STATE=$(su pi --preserve-environment -c "cd /home/pi/nycts-unit && git pull" > "Already up to date." &&  echo ok || echo bad)
	if [ $GIT_STATE == "bad" ]; then
	  yarn install
	fi
fi

cd /home/pi/nycts-unit/api
sudo pkill -f load.py
node index.js &
sleep 10
cd /home/pi/nycts-unit
sudo python start.py
#sudo python combo.p