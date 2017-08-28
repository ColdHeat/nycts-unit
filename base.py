import threading
import time
import urllib
import json
from rgbmatrix import RGBMatrix

class base:
    interval  = 3 # Default polling interval = 2 minutes
    initSleep = 0   # Stagger polling threads to avoid load spikes

    def __init__(self, client):
        self.matrix = RGBMatrix(32, 4)
        self.line = "#"
        self.power = 'on'
        self.matrix.brightness = 50
        self.client        = client
        self.lastQueryTime = time.time()
        t                  = threading.Thread(target=self.thread)
        t.daemon           = True
        t.start()

    # Periodically get predictions from server ---------------------------
    def thread(self):
        initSleep          = 3
        base.initSleep += 5   # Thread staggering may
        #time.sleep(initSleep)    # drift over time, no problem
        while True:

            parsed = base.req(self.client)
            base.getConfig()
            if parsed is None: return     # Connection error

            self.lastQueryTime = time.time()

            #self.matrix.brightness = int(parsed['data']['brightness'])
            self.power = parsed['data']['power']
            self.line  = parsed['data']['line']

            time.sleep(base.interval)

    # Open URL, send request, read & parse XML response ------------------
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
    @staticmethod
    def getConfig():
        baseurl = "http://127.0.0.1:3000/getConfig"
        try:
            result = urllib2.urlopen(baseurl)
            # logger.info('API Config', extra={'status': 1, 'job': 'api_config'})
        except urllib2.URLError as e:
            print e
            # logger.info('API Config', extra={'status': 0, 'job': 'api_config'})
        else:
            config = json.loads(result.read())
        self.matrix.brightness = config["settings"]["brightness"]
    # Set polling interval (seconds) -------------------------------------
    @staticmethod
    def setInterval(i):
        interval = i
