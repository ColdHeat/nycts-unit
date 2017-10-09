import os
import logs
import json
import urllib2
from base import base

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
