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

def check_reboot_status():
    config = load_config_file()
    if config['settings']['reboot'] == True:
        reboot_system()

def reboot_system():
    try:
        result = urllib2.urlopen(
            "http://127.0.0.1:3000/setConfig/settings/reboot/false")
    except urllib2.URLError as e:
        logs.logger.info('System Reboot',
            extra={'status': 0, 'job': 'system_reboot', 'error': str(e)})
    os.system("sudo reboot now")

check_reboot_status()
