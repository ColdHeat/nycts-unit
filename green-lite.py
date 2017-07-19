import atexit
import Image
import ImageDraw
import ImageFont
import math
import os
import time
import urllib
import signal
import json
import logging
from rgbmatrix import RGBMatrix

##### MATRIX #####
width          = 64
height         = 32

matrix                   = RGBMatrix(32, 2) # rows, chain length
matrix.brightness        = 50
#matrix.pwmBits           = 3
#matrix.luminanceCorrect  = False

##### IMAGE / COLORS / FONTS / OFFSET #####
image     = Image.new('RGB', (width, height))
draw      = ImageDraw.Draw(image)

orange    = (255, 100, 0)
green     = (0,   255, 0)
black     = (0,     0, 0)
red       = (255,   0, 0)
font      = ImageFont.load(os.path.dirname(os.path.realpath(__file__)) + '/helvR08.pil')

fontXoffset = 0

slideLength = 10

##### HANDLERS #####
def signal_handler(signal, frame):
    matrix.Clear()
    sys.exit(0)

def clearOnExit():
    matrix.Clear()

def drawClear():
    draw.rectangle((0, 0, width, height), fill=black)
    matrix.SetImage(image, 0, 0)

def displayError():
    drawClear()
    draw.text((0 + fontXoffset + 3,  0), 'WiFi Connection Error', font=font, fill=orange)
    matrix.SetImage(image, 0, 0)
    time.sleep(5)

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

while True:
    try:
        connection = urllib.urlopen('http://riotpros.com/mta/mta/green-lite.php')
        raw = connection.read()
        connection.close()

        parsed = json.loads(raw)

        for dirs,direction in enumerate(parsed):
            drawClear()
            for row in [0, 1]:

                data = parsed[direction][row]

                xOff = 2
                yOff = 2
                
                mins = str(data['min'])
                if len(mins) < 2:
                    mins = mins.rjust(3)

                minLabel = mins + 'min'
                dirLabel = '  ' + data['term']

                nums = data['line']

                if row == 1:
                    yOff = 18

                fontXoffset = xOff
                fontYoffset = yOff

                #numLabel = str(row + 1) + '. '
                #numLabelW = font.getsize(numLabel)[0]

                minPos = width - font.getsize(minLabel)[0] - 3
            
                circleXoffset = fontXoffset #+ numLabelW
                circleYoffset = yOff + 1;

                circleXend = circleXoffset + 8
                circleYend = circleYoffset + 8
            
                #draw.text((fontXoffset, fontYoffset), numLabel, font=font, fill=green)
                draw.ellipse((circleXoffset, circleYoffset, circleXend, circleYend), fill=green)
                draw.text((circleXoffset + 1, circleYoffset - 2), nums, font=font, fill=black)
                draw.text((circleXend, fontYoffset), dirLabel, font=font, fill=green)
                draw.text((minPos, fontYoffset), minLabel, font=font, fill=green)

            matrix.SetImage(image, 0, 0)
            time.sleep(slideLength)

    except Exception as e:
        logging.exception("message")
        displayError()
        time.sleep(5)
        pass