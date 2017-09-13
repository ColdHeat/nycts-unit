import threading
import time
import urllib
import json
import urllib2
import Image
import ImageDraw
import constants
import requests
import logs
import subprocess
import psutil

class systemlogs:

    def __init__(self, base):
        self.base          = base
        self.config        = base.config
        t                  = threading.Thread(target=self.thread)
        t.daemon           = True
        t.start()

    def osLogs(self):
        logs.logger.info('System Diagnostic', extra={'cpu_usage': psutil.cpu_percent(interval=1),
        'virtual_memory': psutil.virtual_memory()[2], 'swap_memory': psutil.swap_memory()[3],
        'disk_usage': psutil.disk_usage('/')[3], 'temp': str((int(subprocess.check_output(['cat', '/sys/class/thermal/thermal_zone0/temp']))/1000) * 9/5 + 32) + ' F',
        })

    def internetSpeedLog(self):
        speed_data = subprocess.check_output(['speedtest-cli', '--json'])
        logs.logger.info('Internet Speed', extra={'speed_test': speed_data})

    def thread(self):
        while True:
            self.config = self.base.config

            self.osLogs()

            self.internetSpeedLog()

            time.sleep(300)
