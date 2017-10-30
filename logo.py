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
    def loadImageFromFile(self):
        try:
            self.pic = Image.open("./api/uploads/0")
            self.pic.thumbnail((128,32), Image.ANTIALIAS)
        except Exception, e:
            logs.logger.info(
                'Logo module', extra={
                    'status': 0,
                    'job': 'logo_module',
                    'error': str(e)
                    })
            self.getImageURL()
    def fetchImage(self, link):
        image = urllib.URLopener()
        try:
            image.retrieve(link, "./api/uploads/0")
            self.pic = Image.open("./api/uploads/0")
            self.pic.thumbnail((128,32), Image.ANTIALIAS)
        except Exception, e:
            logs.logger.info(
                'Logo module', extra={
                    'status': 0,
                    'job': 'logo_module',
                    'error': str(e)
                    })
    def getImageURL():
        try:
            url = 'https://api.trainsignapi.com/prod-trains/stations/' + self.config['subway']['train']
            querystring = {'': ''}
            headers = {
                'x-api-key': self.config['settings']['dev_api_key']
                }
            response = requests.request(
                'GET', url, headers=headers, params=querystring)

            fetchImage(json.loads(response.text)['link'])

        except Exception, e:

            logs.logger.info(
                'Logo module', extra={
                    'status': 0,
                    'job': 'logo_module',
                    'error': str(e)
                    })
    def draw(self):
        self.config = self.base.config
        if self.config["logo"]["updated"] == True:
            baseurl = "http://127.0.0.1:3000/setConfig/logo/updated/false"
            try:
                result = urllib2.urlopen(baseurl, timeout = 5)
            except urllib2.URLError as e:
                error_message = e.reason
                logs.logger.info('API logo module', extra={'status': 0, 'job': 'api_logo_update', 'error': str(e)})
            else:
                self.getImageURL()

        self.base.matrix.SetImage(self.pic.convert('RGB'), 0, 0)
        time.sleep(self.base.getTransitionTime())
