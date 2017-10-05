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
        fail_count = 0

        if fail_count > 10:
            fail_count = 0
            pass
        else:
            try:
                logs.logger.info('System Diagnostic', extra={'status': 1, 'cpu_usage': psutil.cpu_percent(interval=1),
                'virtual_memory': psutil.virtual_memory()[2], 'swap_memory': psutil.swap_memory()[3],
                'disk_usage': psutil.disk_usage('/')[3], 'temp': str((int(subprocess.check_output(['cat', '/sys/class/thermal/thermal_zone0/temp']))/1000) * 9/5 + 32) + ' F',
                })
            except Exception as e:
                logs.logger.info('System Diagnostic', extra={'status': 0, 'job':'system_logs', 'error': str(e)})

            fail_count += 1

    def internetSpeedLog(self):
        fail_count = 0

        if fail_count > 10:
            fail_count = 0
            pass
        else:
            try:
                speed_data = subprocess.check_output(['speedtest-cli', '--json'])
            except Exception as e:
                logs.logger.info('Speed Test', extra={'status': 0, 'job':'speed_test', 'error': str(e)})

            fail_count += 1

    def thread(self):
        while True:
            self.config = self.base.config

            if self.config["settings"]["run_speed_test"] == True:
                self.osLogs()
                self.internetSpeedLog()
            else:
                self.osLogs()

            time.sleep(300)
