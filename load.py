# encoding=utf8
import atexit
import Image
import ImageDraw
import ImageFont
import threading
import os
import time
import signal
import constants
from rgbmatrix import RGBMatrix

class load:

    def __init__(self, base):
        self.base = base
        self.config = base.config

    def draw(self):
        image = Image.new('RGB', (constants.width, constants.height))
        draw  = ImageDraw.Draw(image)
        draw.text((2, 0), 'NYC TRAIN SIGN'  , font=constants.font, fill=constants.red)
        draw.text((68, 0), ' legit. realtime.'  , font=constants.font, fill=constants.green)
        draw.text((2, 16), 'Loading...', font=constants.font, fill=constants.red)
        self.base.matrix.SetImage(image, 0, 0)
