# encoding=utf8
import atexit
import Image
import ImageDraw
import ImageFont
import os
import time
import signal
import constants
from rgbmatrix import RGBMatrix

class load:

    def __init__(self, base):
        self.base = base
        self.config = base.config
        t = threading.Thread(target=self.thread)
        t.daemon = True
        t.start()

    def thread(self):
        while True:

            def draw(self):
                swapImage = Image.new('RGB', (constants.width, constants.height))
                swapDraw  = ImageDraw.Draw(swapImage)
                swapDraw.text((2, 0), 'NYC TRAIN SIGN'  , font=constants.font, fill=constants.red)
                swapDraw.text((68, 0), ' legit. realtime.'  , font=constants.font, fill=constants.green)
                swapDraw.text((2, 16), 'Loading...', font=constants.font, fill=constants.red)
                swap.SetImage(swapImage, 0, 0)
                swap = b.SwapOnVSync(swap)
