import threading
import time
import urllib
import json
import urllib2
import os
import logs
from rgbmatrix import RGBMatrix

class base:
    interval  = 3
    initSleep = 0

    def __init__(self):
        self.matrix = RGBMatrix(32, 4)
        self.line = "#"
        self.power = 'on'
        self.matrix.brightness = 50
        self.lastQueryTime = time.time()
        self.config        = self.getConfig()
        self.client        = self.config["settings"]["client_id"]
        t                  = threading.Thread(target=self.thread)
        t.daemon           = True
        t.start()

    def thread(self):
        initSleep          = 3
        base.initSleep    += 5
        while True:

            parsed = base.req(self.client)
            self.config = self.getConfig()
            self.matrix.brightness = int(self.config["settings"]["brightness"])

            if self.config["settings"]["reboot"] == True:
                baseurl = "http://127.0.0.1:3000/setConfig/settings/reboot/false"
                try:
                    result = urllib2.urlopen(baseurl)
                except urllib2.URLError as e:
                    logs.logger.info('API Reboot', extra={'status': 0, 'job': 'api_reboot'})
                else:
                    os.system('reboot now')

            if parsed is None: return

            self.lastQueryTime = time.time()

            self.power = parsed['data']['power']
            self.line  = parsed['data']['line']

            time.sleep(0.1)

    @staticmethod
    def req(client):
        parsed = None
        try:
            connection = urllib.urlopen(
              'http://riotpros.com/mta/v1/client.php?client=' + client)
            raw = connection.read()
            connection.close()
            parsed = json.loads(raw)
        except Exception,e: print "errr" + str(e)
        finally:
            return parsed
    def getConfig(self):
        baseurl = "http://127.0.0.1:3000/getConfig"
        try:
            result = urllib2.urlopen(baseurl)
        except urllib2.URLError as e:
            logs.logger.info('API Config', extra={'status': 0, 'job': 'api_config'})
        else:
            config = json.loads(result.read())
        return config
    def getTransitionTime(self):
        return int(self.config["settings"]["transition_time"])

    @staticmethod
    def setInterval(i):
        interval = i
