import os
import json
import urllib2
import requests

import sys
sys.path.insert(0, '/home/pi/nycts-unit')
from base import base, logs

def check_wifi_adapter():
    if os.system("ping -c 1 google.com") > 0:
        logs.logger.info('WiFi Shutdown',
            extra={'status': 1, 'job': 'wifi_reboot'})
        reboot_wifi()
    check_device_state()

def check_device_state():
    if base().config['settings']['state'] == 'offline':
        set_device_state(state='online')

def reboot_wifi():
    os.system("sudo /sbin/ifdown 'wlan0' && sleep 5")
    os.system("sudo /sbin/ifup --force 'wlan0' && sleep 5")
    set_device_state(state='online')

def set_device_state(state):
    try:
        result = urllib2.urlopen(
            "http://127.0.0.1:3000/setConfig/settings/state/" + state)
    except urllib2.URLError as e:
        logs.logger.info('API Reboot',
            extra={'status': 0, 'job': 'api_reboot', 'error': str(e)})
        os.system("sudo reboot now")

check_wifi_adapter()
sys.exit()
