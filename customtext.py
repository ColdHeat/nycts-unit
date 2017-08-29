import threading
import time
import urllib
import json
import urllib2
import Image
import ImageDraw
import constants

class customtext:

    def __init__(self, base):
        self.base          = base
        self.config        = base.getConfig()

    def draw(self):
        image = Image.new('RGB', (constants.width, constants.height))
        draw  = ImageDraw.Draw(draw)
        draw.text((2, 0), self.config["customtext"]["line_1"] , font=constants.font, fill=constants.red)
        draw.text((2, 16), self.config["customtext"]["line_2"] , font=contstants.font, fill=constants.blue)
        self.base.matrix.SetImage(image, 0, 0)
