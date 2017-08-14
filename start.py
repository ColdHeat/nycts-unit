# encoding=utf8
import math
import os
import time
import logging
import json

import urllib
import urllib2
from base import base
from log import config_log
from display import *
# from fallback import fallback
from boot import config_matrix
from api import config_api
from train import initialize_train
from weather import weather
# from error import error

client = 29
b = base(client)
logger = log.config_log()


while True:
    def boot(b):
        try:
            boot.config_matrix(b, config, logger)
            logger.info('Booting Up', extra={'status': 1, 'job': 'boot_screen'})
        except Exception as e:
            logger.info('Booting Up', extra={'status': 0, 'job': 'boot_screen'})

    def api(b):
        api.config_api(logger)

    def train(b):
        train.initialize_train(b, logger)
        weatherb, logger()


    def weather(b, logger):
        train(b, logger)
        text(b, logger)

    def text(b):
        swap.Clear()
        textImage = Image.new('RGB', (width, height))
        textDraw  = ImageDraw.Draw(textImage)
        textDraw.text((2, 0), config["text_line_1"] , font=font, fill=red)
        textDraw.text((2, 16), config["text_line_2"] , font=font, fill=blue)
        swap.SetImage(textImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)
        train()
