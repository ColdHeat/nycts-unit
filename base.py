import threading
import time
import urllib
import json
import urllib2
import os
import logs
from rgbmatrix import RGBMatrix, RGBMatrixOptions

options = RGBMatrixOptions()
options.gpio_slowdown = 2
options.pwm_bits = 10
options.hardware_mapping = 'adafruit-hat-pwm'

class base:
    interval  = 3
    initSleep = 0
    def __init__(self):
        self.matrix = RGBMatrix(32, 4, options = options)
        self.matrix.brightness = 50
        self.lastQueryTime = time.time()
        self.config        = self.getConfig()
        self.client        = self.config["settings"]["client_id"]
        self.logs          = logs
        t                  = threading.Thread(target=self.thread)
        t.daemon           = True
        t.start()

    def thread(self):
        initSleep          = 3
        base.initSleep    += 5
        while True:
            self.config = self.getConfig()
            self.matrix.brightness = int(self.config["settings"]["brightness"])
            self.lastQueryTime = time.time()

            time.sleep(0.1)

    def getConfig(self):
        baseurl = "http://127.0.0.1:3000/getConfig"

        try:
            result = urllib2.urlopen(baseurl)
        except urllib2.URLError as e:
            logs.logger.info('API Config',
                extra={'status': 0, 'job': 'api_config', 'error': str(e)})
        else:
            config = json.loads(result.read())
        return config

    def getTransitionTime(self):
        return int(self.config["settings"]["transition_time"])

    @staticmethod
    def setInterval(i):
        interval = i
