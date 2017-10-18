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
import math

class weather:

    def __init__(self, base):
        self.base          = base
        self.config        = base.config
        self.weather       = {'weather': '75',
                              'conditions': 'SUNNY',
                              'state': 'demo'}
        self.start         = time.time()
        t                  = threading.Thread(target=self.thread)
        t.daemon           = True
        t.start()

    def queryWeatherEndpoint(self):
        try:
            url = \
                'https://api.trainsignapi.com/prod-weather/weather/zipCode/' \
                + self.config["weather"]["zip_code"]
            querystring = {"":""}
            headers = {'x-api-key': self.config["settings"]["prod_api_key"]}
            response = requests.request(
                'GET', url, headers=headers, params=querystring)

            data = json.loads(response.text)
            self.weather["weather"] = str(int(data['data']['temperature']))
            self.weather["conditions"] = str(data['data']['summary']).upper()
            self.weather["state"] = "live"

        except Exception as e:
            logs.logger.info(
                'Weather module', extra={
                    'status': 0,
                    'job': 'weather_module',
                    'error': str(e)
                })

    def thread(self):
        while True:
            self.config = self.base.config

            while self.config['settings']['state'] == 'online':
                self.queryWeatherEndpoint()
                time.sleep(120)

    def draw(self):
        image = Image.new('RGB', (constants.width, constants.height))
        draw  = ImageDraw.Draw(image)

        draw.text(
            (2, 0),
            'IT IS ' + self.weather["weather"] + ' DEGREES' ,
            font=constants.font, fill=constants.red
        )
        draw.text(
            (2, 16),
            '& ' + self.weather["conditions"] + ' OUTSIDE',
            font=constants.font, fill=constants.green
        )

        self.base.matrix.SetImage(image, 0, 0)
        time.sleep(self.base.getTransitionTime())
