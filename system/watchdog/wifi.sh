#!/bin/bash

ping -c4 google.com > /dev/null

if [ $? != 0 ]
then
  echo "No network connection, restarting wlan0"
  sudo /sbin/ifdown 'wlan0'
  sleep 5
  sudo /sbin/ifup --force 'wlan0'
fi
