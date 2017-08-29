import threading
import time
import urllib
import json
import urllib2
import Image
import ImageDraw
import constants

class weather:

    def __init__(self, base):
        self.base          = base
        self.config        = base.getConfig()
        self.weather       = {'weather': '75', 'conditions': 'SUNNY'}
        t                  = threading.Thread(target=self.thread)
        t.daemon           = True
        t.start()

    # Periodically get predictions from server ---------------------------
    def thread(self):
        while True:
            baseurl = "https://query.yahooapis.com/v1/public/yql?"
            yql_query = "select item.condition from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + self.config["weather"]["zip_code"] + "')"
            yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
            try:
                result = urllib2.urlopen(yql_url, timeout=5)
                # logger.info('Weather Screen', extra={'status': 1, 'job': 'weather_screen'})
            except urllib2.URLError as e:
                error_message = e.reason
                # logger.info('Weather Screen', extra={'status': 0, 'job': 'weather_screen'})
            else:
                data = json.loads(result.read())
                weather = data['query']['results']['channel']['item']['condition']['temp']
                conditions = data['query']['results']['channel']['item']['condition']['text'].upper()

                self.weather['weather'] = weather
                self.weather['conditions'] = conditions

            time.sleep(5)

    def draw(self):
        image = Image.new('RGB', (constants.width, constants.height))
        draw  = ImageDraw.Draw(image)

        draw.text((2, 0), 'IT IS ' + self.weather["weather"] + ' DEGREES' , font=constants.font, fill=constants.red)
        draw.text((2, 16), '& ' + self.weather["conditions"] + ' OUTSIDE', font=constants.font, fill=constants.green)

        self.base.matrix.SetImage(image, 0, 0)
