import threading
import time
import urllib
import json
import urllib2
import Image
import ImageDraw
import constants

class logo:

    def __init__(self, base):
        self.base          = base
        self.config        = base.getConfig()
        self.pic = Image.open("./api/uploads/" + self.config["logo"]["image_file"])
        self.pic.thumbnail((128,32), Image.ANTIALIAS)


    def draw(self):
        if self.config["logo"]["updated"] == True:
            baseurl = "http://127.0.0.1:3000/setConfig/logo/updated/false"
            try:
                result = urllib2.urlopen(baseurl)
                # logger.info('API Logo Updated', extra={'status': 1, 'job': 'api_logo_update'})
            except urllib2.URLError as e:
                error_message = e.reason
                print error_message
                # logger.info('API Logo Updated', extra={'status': 0, 'job': 'api_logo_update'})
            else:
                self.pic = Image.open("./api/uploads/" + self.config["logo"]["image_file"])
                self.pic = self.pic.convert('RGB')
                self.pic.thumbnail((128,32), Image.ANTIALIAS)

        self.base.matrix.SetImage(self.pic.convert('RGB'), 0, 0)
