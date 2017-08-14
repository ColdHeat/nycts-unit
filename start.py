# encoding=utf8
import math
import os
import time
import logging
import json
import urllib
import urllib2
import socket
from base import base
from log import config_log
from display import *
# from fallback import fallback
# from boot import config_matrix
from api import config_api
from train import initialize_train
from weather import weather
# from error import error

client = 29
b = base(client)
logger = log.config_log()


while True:
    def boot():
        dev = config["dev"]
        swap = b.matrix.CreateFrameCanvas()
        transition_time = int(config["transition_time"])
        b.matrix.brightness = int(config["brightness"])
        try:
            swap.Clear()
            swapImage = display.Image.new('RGB', (width, height))
            swapDraw  = display.ImageDraw.Draw(swapImage)
            if dev == True:
                try:
                    ip = str([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
                    logger.info('IP screen', extra={'status': 1, 'job': 'ip_screen'})
                except Exception as e:
                    logger.info('IP screen', extra={'status': 0, 'job': 'ip_screen'})
                    ip = '192.168.0.xxx'

                swapDraw.text((2, 0), 'IP: ' + ip , font=font, fill=red)
            else:
                logger.info('NYC Train Sign', extra={'status': 1, 'job': 'boot_screen'})
                swapDraw.text((2, 0), 'NYC TRAIN SIGN'  , font=display.font, fill=display.red)
                swapDraw.text((68, 0), ' legit. realtime.'  , font=display.font, fill=display.green)
                swapDraw.text((2, 16), '@' , font=display.font, fill=display.green)
                swapDraw.text((12, 16), 'n y c t r a i n s i g n' , font=display.font, fill=display.orange)
            swap.SetImage(swapImage, 0, 0)
            time.sleep(transition_time)
            swap = b.matrix.SwapOnVSync(swap)

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
