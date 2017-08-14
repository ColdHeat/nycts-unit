# encoding=utf8
import math
import os
import time
import logging
import json
import socket
import urllib
import urllib2
from base import base
from log import log
from display import display
from image import image
from fallback import fallback
from boot import boot
from api import api
from train import train
from weather import weather
from error import error

client = 29
b = base(client)
log.config_log()
display.function()
image.function()
fallback.function()

while True:
    def boot():
        try:
            boot.config_matrix(b, config)
            logger.info('Booting Up', extra={'status': 1, 'job': 'boot_screen'})
        except Exception as e:
            logger.info('Booting Up', extra={'status': 0, 'job': 'boot_screen'})

    def api():
        api.config_api

    def train():
        train.initialize_train
        weather()
        text()

    def weather():
        train()

    def text():
        swap.Clear()
        textImage = Image.new('RGB', (width, height))
        textDraw  = ImageDraw.Draw(textImage)
        textDraw.text((2, 0), config["text_line_1"] , font=font, fill=red)
        textDraw.text((2, 16), config["text_line_2"] , font=font, fill=blue)
        swap.SetImage(textImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)
        train()


    except Exception as e:
        #throw exception from excption script
