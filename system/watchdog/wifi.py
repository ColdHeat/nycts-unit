import os
import json
import urllib2
import requests
import sys
sys.path.insert(0, '/home/pi/nycts-unit')
print sys.path
from base import base

def check_if_offline():
    if base().config['settings']['state'] == 'offline':
        pass
    else:
        check_wifi_adapter()

def check_wifi_adapter():
    response = os.system("ping -c 1 google.com")

    if response > 0:
        logs.logger.info('WiFi Shutdown',
            extra={'status': 1, 'job': 'wifi_reboot'})
        turn_wifi_off()

def turn_wifi_off():
    os.system("sudo /sbin/ifdown 'wlan0' && sleep 5")
    os.system("sudo /sbin/ifup --force 'wlan0' && sleep 5")

    try:
        result = urllib2.urlopen(
            "http://127.0.0.1:3000/setConfig/settings/state/online")
    except urllib2.URLError as e:
        logs.logger.info('API Reboot',
            extra={'status': 0, 'job': 'api_reboot', 'error': str(e)})

check_if_offline()
