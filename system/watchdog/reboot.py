import os
import json
import urllib2

import sys
sys.path.insert(0, '/home/pi/nycts-unit')
from base import base, logs

def check_reboot_status():
    if base().config['settings']['reboot'] == False:
        pass
    else:
        reboot_system()

def reboot_system():
    try:
        result = urllib2.urlopen(
            "http://127.0.0.1:3000/setConfig/settings/reboot/false"
        )
    except urllib2.URLError as e:
        logs.logger.info('System Reboot',
            extra={'status': 0, 'job': 'system_reboot', 'error': str(e)})

    os.system("sudo reboot now")

check_reboot_status()
