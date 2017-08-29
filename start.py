# encoding=utf8
import atexit
import Image
import ImageDraw
import ImageFont
import math
import os
import time
import signal
import logging
import json
import json_log_formatter
import socket
import urllib
import urllib2
from base import base
from weather import weather
from customtext import customtext
from logo import logo
from ad import ad
from train import train

### LOGGING ###
# formatter = json_log_formatter.JSONFormatter()
#
# json_handler = logging.FileHandler(filename='./device_logs/logs.json')
# json_handler.setFormatter(formatter)
#
# logger = logging.getLogger('log')
# logger.addHandler(json_handler)
# logger.setLevel(logging.INFO)
# logger.info('Booting Up', extra={'status': 1, 'job': 'boot_screen'})


##### LOAD CONFIG #######
baseurl = "http://127.0.0.1:3000/getConfig"
try:
    result = urllib2.urlopen(baseurl)
    # logger.info('API Config', extra={'status': 1, 'job': 'api_config'})
except urllib2.URLError as e:
    print e
    # logger.info('API Config', extra={'status': 0, 'job': 'api_config'})
else:
    config = json.loads(result.read())
##### CLIENT CONFIGURATION #####
client = config["settings"]["client_id"]

b = base(client)
weatherScreen = weather(b)
customTextScreen = customtext(b)
logoScreen = logo(b)
adScreen = ad(b)
trainScreen = train(b)

##### MATRIX #####
width          = 128
height         = 32

##### IMAGE / COLORS / FONTS / OFFSET #####
image     = Image.new('RGB', (width, height))
draw      = ImageDraw.Draw(image)

black     = (0,     0, 0)
blue      = (0, 200, 255)
green     = (0,   255, 0)
grey      = (105,105,105)
orange    = (255, 100, 0)
red       = (255,   0, 0)
yellow    = (252, 203, 7)

font      = ImageFont.load(os.path.dirname(os.path.realpath(__file__)) + '/helvR08.pil')

fontXoffset = 0
topOffset   = 3

lLabel = 'L '

lOffset = 4
minLabel = 'MIn'
minOffset = width - 6 - font.getsize(minLabel)[0]

count = True

##### HANDLERS #####
def signal_handler(signal, frame):
    b.matrix.Clear()
    sys.exit(0)

def clearOnExit():
    b.matrix.Clear()

def drawClear():
    draw.rectangle((0, 0, width, height), fill=black)
    b.matrix.SetImage(image, 0, 0)

def displayError(e):
    drawClear()
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), e, font=font, fill=orange)
    b.matrix.SetImage(image, 0, 0)
    time.sleep(transition_time)
    drawClear()

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

swap = b.matrix.CreateFrameCanvas()


start = time.time()

backup_train_data = {"N":[{"line":"R","min":6,"term":"Queens "},{"line":"N","min":7,"term":"Astoria "}],"S":[{"line":"R","min":2,"term":"Whitehall "},{"line":"N","min":6,"term":"Coney Island "}]}

while True:

    baseurl = "http://127.0.0.1:3000/getConfig"
    try:
        result = urllib2.urlopen(baseurl)
        # logger.info('API Config', extra={'status': 1, 'job': 'api_config'})
    except urllib2.URLError as e:
        print e
        # logger.info('API Config', extra={'status': 0, 'job': 'api_config'})
    else:
        config = json.loads(result.read())


    if b.config["settings"]["reboot"] == True:
        baseurl = "http://127.0.0.1:3000/setConfig/settings/reboot/false"
        try:
            result = urllib2.urlopen(baseurl)
            # logger.info('API Reboot', extra={'status': 1, 'job': 'api_reboot'})
        except urllib2.URLError as e:
            error_message = e.reason
            print error_message
            # logger.info('API Reboot', extra={'status': 0, 'job': 'api_reboot'})
        else:
            os.system('reboot now')

    transition_time = int(b.config["settings"]["transition_time"])

    ##### BOOT SCREEN #####
    try:
        swap.Clear()
        adScreen.draw()
        time.sleep(transition_time)

    ##### CUSTOM TEXT SCREEN #####
        swap.Clear()
        customTextScreen.draw()
        time.sleep(transition_time)

    ##### WEATHER SCREEN #####
        swap.Clear()
        weatherScreen.draw()
        time.sleep(transition_time)

    ##### TRAIN SCREEN #####

        swap.Clear()
        time.sleep(transition_time)


    #### LOGO #####
        swap.Clear()
        logoScreen.draw()
        time.sleep(transition_time)


##### EXCEPTION SCREEN #####
    except Exception as e:
        logging.exception("message")
        # logger.info('Boot Screen', extra={'status': 1, 'job': 'boot_screen'})
        displayError(e)
        pass
