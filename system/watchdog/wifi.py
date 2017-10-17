import os
import json
import urllib2
import requests

import sys
sys.path.insert(0, '/home/pi/nycts-unit')
from base import base, logs

def check_if_offline():
    if base().config['settings']['state'] == 'online':
        check_wifi_adapter()
    else:
        set_state_online()

def check_wifi_adapter():
    if os.system("ping -c 1 google.com") > 0:
        logs.logger.info('WiFi Shutdown',
            extra={'status': 1, 'job': 'wifi_reboot'})
        turn_wifi_off()

def turn_wifi_off():
    os.system("sudo /sbin/ifdown 'wlan0' && sleep 5")
    os.system("sudo /sbin/ifup --force 'wlan0' && sleep 5")
    set_state_online()

def set_state_online():
    try:
        result = urllib2.urlopen(
            "http://127.0.0.1:3000/setConfig/settings/state/online")
    except urllib2.URLError as e:
        logs.logger.info('API Reboot',
            extra={'status': 0, 'job': 'api_reboot', 'error': str(e)})
        os.system("sudo reboot now")

check_if_offline()
