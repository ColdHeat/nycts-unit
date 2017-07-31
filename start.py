# encoding=utf8
import atexit
import Image
import ImageDraw
import ImageFont
import math
import os
import time
import urllib
import signal
import logging
import json
import socket
import urllib2
from base import base

#with open('config.json') as config_file:
#    config = json.load(config_file)
config = json.loads('{}')
baseurl = "https://127.0.0.1:3000/"
try:
    result = urllib2.urlopen(baseurl)
except urllib2.URLError as e:
    print 'error'
else:
    config = json.loads(result.read())


print config
##### DEV MODE #####
dev = config["dev"]

client = '29'
b = base(client)

transition_time = config["transition_time"]
##### MATRIX #####
width          = 128
height         = 32


##### IMAGE / COLORS / FONTS / OFFSET #####
image     = Image.new('RGB', (width, height))
draw      = ImageDraw.Draw(image)

orange    = (255, 100, 0)
green     = (0,   255, 0)
black     = (0,     0, 0)
red       = (255,   0, 0)
blue      = (0,     200, 255)

font      = ImageFont.load(os.path.dirname(os.path.realpath(__file__)) + '/helvR08.pil')

fontXoffset = 0
topOffset   = 3

lLabel = 'L '

lOffset = 4
minLabel = 'MIn'
minOffset = width - 6 - font.getsize(minLabel)[0]

count = True

slideLength = 10

pic = Image.open("emoji.png")
pic = pic.convert('RGB')
pic.thumbnail((128,32), Image.ANTIALIAS)

weather = '74'
conditions = 'Mostly Sunny'

##### HANDLERS #####
def signal_handler(signal, frame):
    b.matrix.Clear()
    sys.exit(0)

def clearOnExit():
    b.matrix.Clear()

def drawClear():
    draw.rectangle((0, 0, width, height), fill=black)
    b.matrix.SetImage(image, 0, 0)

def displayError():
    drawClear()
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), 'WiFi Connection Error', font=font, fill=orange)
    b.matrix.SetImage(image, 0, 0)
    time.sleep(transition_time)
    drawClear()

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

swap = b.matrix.CreateFrameCanvas()

while True:

    try:

        swap.Clear()
        swapImage = Image.new('RGB', (width, height))
        swapDraw  = ImageDraw.Draw(swapImage)
        if dev == True:
            ip = str([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
            swapDraw.text((2, 0), 'IP: ' + ip , font=font, fill=red)
        else:
            swapDraw.text((2, 0), 'NYC TRAIN SIGN'  , font=font, fill=red)
            swapDraw.text((68, 0), ' legit. realtime.'  , font=font, fill=green)
            swapDraw.text((2, 16), '@' , font=font, fill=green)
            swapDraw.text((12, 16), 'n y c t r a i n s i g n' , font=font, fill=orange)
        swap.SetImage(swapImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)


        swap.Clear()
        textImage = Image.new('RGB', (width, height))
        textDraw  = ImageDraw.Draw(textImage)
        textDraw.text((2, 0), config["text_line_1"] , font=font, fill=red)
        textDraw.text((2, 16), config["text_line_2"] , font=font, fill=blue)
        swap.SetImage(textImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)


        swap.Clear()

        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = "select item.condition from weather.forecast where woeid in (select woeid from geo.places(1) where text='"+ str(config["weather_zip"]) + "')"
        yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
        try:
            result = urllib2.urlopen(yql_url)
        except urllib2.URLError as e:
            print 'error'
        else:
            data = json.loads(result.read())
            weather = data['query']['results']['channel']['item']['condition']['temp']
            conditions = data['query']['results']['channel']['item']['condition']['text'].upper()

        weatherImage = Image.new('RGB', (width, height))
        weatherDraw  = ImageDraw.Draw(weatherImage)



        weatherDraw.text((2, 0), 'IT IS ' + weather + ' FUCKING DEGREES' , font=font, fill=red)
        weatherDraw.text((2, 16), '& ' + conditions + ' OUTSIDE', font=font, fill=green)

        swap.SetImage(weatherImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)

        swap.Clear()

        count = not count

        if count == True:
            frame = 'ln'
        else :
            frame ='ls'

        connection = urllib.urlopen('http://riotpros.com/mta/v1/?client=' + client)
        raw = connection.read()
        times = raw.split()
        connection.close()



        if frame == 'ln':
            dirLabel = '    MANHATTAN '
            dirOffset = 22
        if frame == 'ls':
            dirLabel = '   ROCKAWAY PKWY'
            dirOffset = 12

        if len(times) > 3:
            try:
                val = int(times[0])
            except ValueError:
                min1 = '*'
                min2 = '*'

            if frame == 'ln':
                min1 = times[0]
                min2 = times[1]
            if frame == 'ls':
                min1 = times[2]
                min2 = times[3]
        else:
            min1 = '*'
            min2 = '*'

        if len(min1) < 2:
            min1 = min1.rjust(3)
        time1Offset = minOffset - font.getsize(min1)[0]

        if len(min2) < 2:
            min2 = min2.rjust(3)
        time2Offset = minOffset - font.getsize(min2)[0]

        dirLabelw = font.getsize(dirLabel)[0]
        draw.rectangle((0, 0, width, height), fill=black)
        draw.text((lOffset, 0 + topOffset), lLabel, font=font, fill=orange)
        draw.text((fontXoffset + dirOffset, 0 + topOffset), dirLabel, font=font, fill=green)
        draw.text((time1Offset, 0 + topOffset), min1, font=font, fill=orange)
        draw.text((minOffset, 0 + topOffset), minLabel, font=font, fill=green)

        draw.text((lOffset, 16), lLabel, font=font, fill=orange)
        draw.text((fontXoffset + dirOffset, 16), dirLabel, font=font, fill=green)
        draw.text((time2Offset, 16), min2, font=font, fill=orange)
        draw.text((minOffset, 16), minLabel, font=font, fill=green)

        draw.point((width - 12, 7), fill=black)
        draw.point((width - 12, 20), fill=black)

        swap.SetImage(image, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)

        swap.Clear()
        swap.SetImage(pic.convert('RGB'), 0, 0)

        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)

    except Exception as e:
        logging.exception("message")
        displayError()
        pass
