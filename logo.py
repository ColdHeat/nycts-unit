import threading
import time
import urllib
import json
import urllib2
import Image
import ImageDraw
import constants
import logs

class logo:

    def __init__(self, base):
        self.base          = base
        self.config        = base.config
        self.pic = Image.open("./api/uploads/" + self.config["logo"]["image_file"])
        self.pic.thumbnail((128,32), Image.ANTIALIAS)

    def draw(self):
        self.config = self.base.config
        if self.config["logo"]["updated"] == True:
            baseurl = "http://127.0.0.1:3000/setConfig/logo/updated/false"
            logs.logger.info('API logo module', extra={'status': 1, 'job': 'api_logo_update'})
            try:
                result = urllib2.urlopen(baseurl, timeout = 5)                
            except urllib2.URLError as e:
                error_message = e.reason
                logs.logger.info('API logo module', extra={'status': 0, 'job': 'api_logo_update'})
            else:
                self.pic = Image.open("./api/uploads/" + self.config["logo"]["image_file"])
                self.pic = self.pic.convert('RGB')
                self.pic.thumbnail((128,32), Image.ANTIALIAS)

        self.base.matrix.SetImage(self.pic.convert('RGB'), 0, 0)
        time.sleep(self.base.getTransitionTime())
