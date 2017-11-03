import os
import json
import urllib2
import sys
sys.path.insert(0, '/home/pi/nycts-unit')
import logs

def load_config_file():
    baseurl = "http://127.0.0.1:3000/getConfig"
    try:
        result = urllib2.urlopen(baseurl)
    except urllib2.URLError as e:
        sys.exit()
    config = json.loads(result.read())
    return config

def ping_router():
    if os.system("ping -c 1 google.com") > 0:
        logs.logger.info('WiFi Shutdown',
            extra={'status': 1, 'job': 'wifi_reboot'})
        reboot_wifi()
    set_device_state(state='online')

def reboot_wifi():
    config = load_config_file()
    if config['settings']['state'] == 'online':
        set_device_state(state='offline')
        os.system("sudo /sbin/ifdown 'wlan0'")
        os.system("sudo /sbin/ifup --force 'wlan0' && sleep 10")
    else:
        ping_router()

def set_device_state(state):
    try:
        result = urllib2.urlopen(
            "http://127.0.0.1:3000/setConfig/settings/state/" + state)
    except urllib2.URLError as e:
        logs.logger.info('Set Device State',
            extra={'status': 0, 'job': 'device_state', 'error': str(e)})
        sys.exit()

ping_router()
