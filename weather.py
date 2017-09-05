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

class weather:

    def __init__(self, base):
        self.base          = base
        self.config        = base.config
        self.weather       = {'weather': '75', 'conditions': 'SUNNY'}
        t                  = threading.Thread(target=self.thread)
        t.daemon           = True
        t.start()

    # Periodically get predictions from server ---------------------------
    def thread(self):
        while True:
            try:
                self.config = self.base.config

                url = "https://api.trainsignapi.com/dev-weather/zipCode/11216"

                querystring = {"":""}

                headers = {'x-api-key': '5lz8VPkVUL7gcjN5LsZwu1eArX8A3B2m8VeUfXxf'}

                response = requests.request("GET", url, headers=headers, params=querystring)

                data = json.loads(response.text)
                self.weather["weather"] = str(int(data['data']['temperature']))
                self.weather["conditions"] = str(data['data']['summary']).upper()

                logs.logger.info('Weather module', extra={'status': 1, 'job': 'weather_module'})
            except Exception as e:
                logs.logger.info('Weather module', extra={'status': 0, 'job': 'weather_module'}, exc_info=True)

            time.sleep(5)

    def draw(self):
        image = Image.new('RGB', (constants.width, constants.height))
        draw  = ImageDraw.Draw(image)

        draw.text((2, 0), 'IT IS ' + self.weather["weather"] + ' DEGREES' , font=constants.font, fill=constants.red)
        draw.text((2, 16), '& ' + self.weather["conditions"] + ' OUTSIDE', font=constants.font, fill=constants.green)

        self.base.matrix.SetImage(image, 0, 0)
        time.sleep(self.base.getTransitionTime())
