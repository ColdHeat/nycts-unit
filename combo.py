from base import base
import atexit
import Image
import ImageDraw
import ImageFont
import math
import os
import time
import urllib
import urllib2
import signal
import json
import logging


client = '32'
##### MATRIX #####
width          = 128
height         = 32

b = base(client)
#matrix.pwmBits           = 3
#matrix.luminanceCorrect  = False

##### IMAGE / COLORS / FONTS / OFFSET #####
image     = Image.new('RGB', (width, height))
draw      = ImageDraw.Draw(image)

yellow    = (252, 203, 7)
orange    = (255, 100, 0)
grey      = (105,105,105)
green     = (0,   255, 0)
black     = (0,     0, 0)
red       = (255,   0, 0)
font      = ImageFont.load(os.path.dirname(os.path.realpath(__file__)) + '/helvR08.pil')

fontXoffset = 0

slideLength = 3

transition_time = 6

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
    draw.text((0 + fontXoffset + 3,  0), 'WiFi Connection Error', font=font, fill=orange)
    b.matrix.SetImage(image, 0, 0)
    time.sleep(5)


atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

start = time.time()

backup_train_data = {"N":[{"line":"R","min":6,"term":"Queens "},{"line":"N","min":7,"term":"Astoria "}],"S":[{"line":"R","min":2,"term":"Whitehall "},{"line":"N","min":6,"term":"Coney Island "},{"line":"W","min":6,"term":"Brooklyn "}]}

while True:
    try:
        connection = urllib2.urlopen('http://riotpros.com/mta/v1/?client=' + client)
        raw = connection.read()
        connection.close()

        parsed = json.loads(raw)
        backup_train_data = parsed

    except urllib2.URLError as e:
        end = time.time()

        time_difference = math.ceil(end - start)

        if time_difference > 300:
            start = time.time()

        parsed = backup_train_data
        for dirs,direction in enumerate(parsed):
            drawClear()

            for row in [0, 1]:
                data = parsed[direction][row]

                xOff = 2
                yOff = 2

                mins = str(data['min'])
                if len(mins) < 2:
                    if int(mins) = 0:
                        mins = str(int(mins) + 6)
                    else:
                        mins = str((int(mins) - int(time_difference)/ 60))

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

                draw.text((fontXoffset, fontYoffset), numLabel, font=font, fill=green)
                draw.ellipse((circleXoffset, circleYoffset, circleXend, circleYend), fill=circleColor)
                draw.text((circleXoffset + 1, circleYoffset - 2), nums, font=font, fill=black)
                draw.text((circleXend, fontYoffset), dirLabel, font=font, fill=green)
                draw.text((minPos, fontYoffset), minLabel, font=font, fill=green)

                #draw.point((width - 9, 3), fill=red)
                draw.point((width - 9, 6), fill=black)
                #draw.point((width - 9, 19), fill=red)
                draw.point((width - 9, 22), fill=black)

            b.matrix.SetImage(image, 0, 0)
            time.sleep(transition_time)

    else:
        for dirs,direction in enumerate(parsed):
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

                draw.text((fontXoffset, fontYoffset), numLabel, font=font, fill=green)
                draw.ellipse((circleXoffset, circleYoffset, circleXend, circleYend), fill=circleColor)
                draw.text((circleXoffset + 1, circleYoffset - 2), nums, font=font, fill=black)
                draw.text((circleXend, fontYoffset), dirLabel, font=font, fill=green)
                draw.text((minPos, fontYoffset), minLabel, font=font, fill=green)

                #draw.point((width - 9, 3), fill=red)
                draw.point((width - 9, 6), fill=black)
                #draw.point((width - 9, 19), fill=red)
                draw.point((width - 9, 22), fill=black)

            b.matrix.SetImage(image, 0, 0)
            time.sleep(transition_time)

    # except Exception as e:
    #     logging.exception("message")
    #     displayError()
    #     pass
