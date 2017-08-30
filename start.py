# encoding=utf8
import atexit
import Image
import ImageDraw
import ImageFont
import time
import signal
import logging
import json
import json_log_formatter
from base import base
from weather import weather
from customtext import customtext
from logo import logo
from ad import ad
from train import train
import constants

### LOGGING ###
# formatter = json_log_formatter.JSONFormatter()
# json_handler = logging.FileHandler(filename='./device_logs/logs.json')
# json_handler.setFormatter(formatter)
#
# logger = logging.getLogger('log')
# logger.addHandler(json_handler)
# logger.setLevel(logging.INFO)
# logger.info('Booting Up', extra={'status': 1, 'job': 'boot_screen'})

b = base()
swap = b.matrix.CreateFrameCanvas()

weatherScreen = weather(b)
customTextScreen = customtext(b)
logoScreen = logo(b)
adScreen = ad(b)
trainScreen = train(b)

fontXoffset = 0
topOffset   = 3

image     = Image.new('RGB', (constants.width, constants.height))
draw      = ImageDraw.Draw(image)

##### HANDLERS #####
def signal_handler(signal, frame):
    b.matrix.Clear()
    sys.exit(0)

def clearOnExit():
    b.matrix.Clear()

def drawClear():
    draw.rectangle((0, 0, constants.width, constants.height), fill=constants.black)
    b.matrix.SetImage(image, 0, 0)

def displayError(e):
    drawClear()
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), e, font=constants.font, fill=constants.orange)
    b.matrix.SetImage(image, 0, 0)
    time.sleep(1)
    drawClear()

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

while True:

    ##### BOOT SCREEN #####
    try:
        swap.Clear()
        adScreen.draw()
        time.sleep(b.getTransitionTime())

    ##### CUSTOM TEXT SCREEN #####
        swap.Clear()
        customTextScreen.draw()
        time.sleep(b.getTransitionTime())

    ##### WEATHER SCREEN #####
        swap.Clear()
        weatherScreen.draw()
        time.sleep(b.getTransitionTime())

    ##### TRAIN SCREEN SOUTH #####
        swap.Clear()
        trainScreen.draw('S')
        time.sleep(b.getTransitionTime())

    ##### TRAIN SCREEN NORTH #####
        swap.Clear()
        trainScreen.draw('N')
        time.sleep(b.getTransitionTime())

    #### LOGO #####
        swap.Clear()
        logoScreen.draw()
        time.sleep(b.getTransitionTime())

##### EXCEPTION SCREEN #####
    except Exception as e:
        logging.exception("message")
        # logger.info('Boot Screen', extra={'status': 1, 'job': 'boot_screen'})
        displayError(e)
        pass
