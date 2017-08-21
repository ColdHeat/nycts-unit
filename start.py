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

### LOGGING ###
formatter = json_log_formatter.JSONFormatter()

json_handler = logging.FileHandler(filename='./device_logs/logs.json')
json_handler.setFormatter(formatter)

logger = logging.getLogger('log')
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)
logger.info('Booting Up', extra={'status': 1, 'job': 'boot_screen'})


##### LOAD CONFIG #######
baseurl = "http://127.0.0.1:3000/getConfig"
try:
    result = urllib2.urlopen(baseurl)
    logger.info('API Config', extra={'status': 1, 'job': 'api_config'})
except urllib2.URLError as e:
    logger.info('API Config', extra={'status': 0, 'job': 'api_config'})
else:
    config = json.loads(result.read())
##### CLIENT CONFIGURATION #####
client = config["settings"]["client_id"]

b = base(client)


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

slideLength = 10

pic = Image.open("./api/uploads/"+ config["logo"]["image_file"])
pic = pic.convert('RGB')
pic.thumbnail((128,32), Image.ANTIALIAS)


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

weather_offline_data = {'weather': 75, 'conditions': 'SUNNY'}

start = time.time()

backup_train_data = {"N":[{"line":"R","min":6,"term":"Queens "},{"line":"N","min":7,"term":"Astoria "}],"S":[{"line":"R","min":2,"term":"Whitehall "},{"line":"N","min":6,"term":"Coney Island "}]}

##### NODE API #####
with open("config.json") as json_file:
    config = json.load(json_file)

while True:

    baseurl = "http://127.0.0.1:3000/getConfig"
    try:
        result = urllib2.urlopen(baseurl)
        logger.info('API Config', extra={'status': 1, 'job': 'api_config'})
    except urllib2.URLError as e:
        logger.info('API Config', extra={'status': 0, 'job': 'api_config'})
    else:
        config = json.loads(result.read())

    ##### DEV MODE #####
    dev = config["settings"]["dev"]

    if config["settings"]["reboot"] == "1":
        baseurl = "http://127.0.0.1:3000/setConfig/settings/reboot/0"
        try:
            result = urllib2.urlopen(baseurl)
            logger.info('API Reboot', extra={'status': 1, 'job': 'api_reboot'})
        except urllib2.URLError as e:
            error_message = e.reason
            logger.info('API Reboot', extra={'status': 0, 'job': 'api_reboot'})
        else:
            config = json.loads(result.read())
            os.system('reboot now')


    transition_time = int(config["settings"]["transition_time"])
    b.matrix.brightness = int(config["settings"]["brightness"])

    ##### BOOT SCREEN #####
    try:
        swap.Clear()
        swapImage = Image.new('RGB', (width, height))
        swapDraw  = ImageDraw.Draw(swapImage)
        if dev == True:
            try:
                ip = str([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
                logger.info('IP screen', extra={'status': 1, 'job': 'ip_screen'})
            except Exception as e:
                logger.info('IP screen', extra={'status': 0, 'job': 'ip_screen'}, exc_info=True)
                ip = '192.168.0.xxx'

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
        textDraw.text((2, 0), config["customtext"]["line_1"] , font=font, fill=red)
        textDraw.text((2, 16), config["customtext"]["line_2"] , font=font, fill=blue)
        swap.SetImage(textImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)


    ##### WEATHER SCREEN #####
        swap.Clear()

        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = "select item.condition from weather.forecast where woeid in (select woeid from geo.places(1) where text='"+ str(config["weather"]["zip_code"]) + "')"
        yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
        try:
            result = urllib2.urlopen(yql_url)
            logger.info('Weather Screen', extra={'status': 1, 'job': 'weather_screen'})
        except urllib2.URLError as e:
            error_message = e.reason
            logger.info('Weather Screen', extra={'status': 0, 'job': 'weather_screen'})
            weather = weather_offline_data['weather']
            conditions = weather_offline_data['conditions']
        else:
            data = json.loads(result.read())
            weather = data['query']['results']['channel']['item']['condition']['temp']
            conditions = data['query']['results']['channel']['item']['condition']['text'].upper()

            weather_offline_data['weather'] = weather
            weather_offline_data['conditions'] = conditions

        weatherImage = Image.new('RGB', (width, height))
        weatherDraw  = ImageDraw.Draw(weatherImage)

        weatherDraw.text((2, 0), 'IT IS ' + weather + ' FUCKING DEGREES' , font=font, fill=red)
        weatherDraw.text((2, 16), '& ' + conditions + ' OUTSIDE', font=font, fill=green)

        swap.SetImage(weatherImage, 0, 0)
        time.sleep(transition_time)
        swap = b.matrix.SwapOnVSync(swap)

    ##### TRAIN SCREEN #####

        try:
            connection = urllib2.urlopen('http://riotpros.com/mta/v1/combo.php?client=' + client)
            logger.info('Train Screen', extra={'status': 1, 'job': 'train_screen'})
            raw = connection.read()
            parsed = json.loads(raw)
            connection.close()
            backup_train_data = parsed
        except Exception as e:

            end = time.time()

            time_difference = math.ceil(end - start)

            if time_difference >= 60:
                start = time.time()
                end = time.time()

            parsed = backup_train_data

            if len(mins) < 3:
                if data['min'] <= 0:
                    mins = str((int(data['min']) + 6))
                    data['min'] = int(mins)
                else:
                    mins = str((int(data['min']) - int(time_difference)/ 60))
                    data['min'] = int(mins)

            error_message = e.reason
            logger.info('Train Screen', extra={'status': 0, 'job': 'train_screen', 'error': error_message})


        for dirs,direction in enumerate(parsed):
            time.sleep(transition_time)
            drawClear()

            for row in [0, 1]:
                data = parsed[direction][row]

                xOff = 2
                yOff = 2

                mins = str(data['min'])
                if len(mins) < 2:
                    mins = mins.rjust(3)

                minLabel = mins + 'mIn'
                dirLabel = '  ' + data['term']

                nums = data['line']

                if nums in ['1', '2', '3']:
                    circleColor = red
                if nums in ['4', '5', '6']:
                    circleColor = green
                if nums in ['N', 'Q', 'R', 'W']:
                    circleColor = yellow
                if nums in ['L']:
                    circleColor = grey

                if row == 1:
                    yOff = 18

                fontXoffset = xOff
                fontYoffset = yOff

                numLabel = str(row + 1) + '. '
                numLabelW = font.getsize(numLabel)[0]

                minPos = width - font.getsize(minLabel)[0] - 3

                circleXoffset = fontXoffset + numLabelW
                circleYoffset = yOff + 1;

                circleXend = circleXoffset + 8
                circleYend = circleYoffset + 8

                if data['line'] == 'L':
                    dirOffset = 26
                    lLabel = 'L '
                    minLabel = 'MIn'
                    lOffset = 4
                    minOffset = width - 6 - font.getsize(minLabel)[0]
                    timeOffset = minOffset - font.getsize(mins)[0]

                    draw.text((lOffset, 0 + fontYoffset), lLabel, font=font, fill=orange)
                    draw.text((fontXoffset + dirOffset, 0 + fontYoffset), dirLabel, font=font, fill=green)

                    draw.text((timeOffset, 0 + fontYoffset), mins, font=font, fill=orange)
                    draw.text((minOffset, 0 + fontYoffset), minLabel, font=font, fill=green)

                    draw.point((width - 12, 6), fill=black)
                    draw.point((width - 12, 22), fill=black)

                else:
                    draw.text((fontXoffset, fontYoffset), numLabel, font=font, fill=green)
                    draw.ellipse((circleXoffset, circleYoffset, circleXend, circleYend), fill=circleColor)
                    draw.text((circleXoffset + 1, circleYoffset - 2), nums, font=font, fill=black)
                    draw.text((circleXend, fontYoffset), dirLabel, font=font, fill=green)
                    draw.text((minPos, fontYoffset), minLabel, font=font, fill=green)

                    draw.point((width - 9, 6), fill=black)
                    draw.point((width - 9, 22), fill=black)

            b.matrix.SetImage(image, 0, 0)
            time.sleep(transition_time)

            swap = b.matrix.SwapOnVSync(swap)

            #### LOGO #####
            swap.Clear()
            swap.SetImage(pic.convert('RGB'), 0, 0)

            time.sleep(transition_time)

##### EXCEPTION SCREEN #####
    except Exception as e:
        logging.exception("message")
        logger.info('Boot Screen', extra={'status': 1, 'job': 'boot_screen'})
        displayError(e)
        pass
