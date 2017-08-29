import threading
import time
import urllib
import json
import urllib2
import Image
import ImageDraw
import constants

class ad:

    def __init__(self, base):
        self.base          = base
        self.config        = base.getConfig()

    def draw(self):
        image = Image.new('RGB', (constants.width, constants.height))
        draw  = ImageDraw.Draw(image)
        dev = self.config["settings"]["dev"]

        if dev == True:
            try:
                ip = str([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
                # logger.info('IP screen', extra={'status': 1, 'job': 'ip_screen'})
            except Exception as e:
                # logger.info('IP screen', extra={'status': 0, 'job': 'ip_screen'}, exc_info=True)
                ip = '192.168.0.xxx'

            draw.text((2, 0), 'IP: ' + ip , font=constants.font, fill=constants.red)
        else:
            draw.text((2, 0), 'NYC TRAIN SIGN'  , font=constants.font, fill=constants.red)
            draw.text((68, 0), ' legit. realtime.'  , font=constants.font, fill=constants.green)
            draw.text((2, 16), '@' , font=constants.font, fill=constants.green)
            draw.text((12, 16), 'n y c t r a i n s i g n' , font=constants.font, fill=constants.orange)
        self.base.matrix.SetImage(image, 0, 0)
