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

orange    = (255, 70, 0)
green     = (0,   255, 0)
black     = (0,     0, 0)

font      = ImageFont.load(os.path.dirname(os.path.realpath(__file__)) + '/helvR08.pil')

fontXoffset = 0
topOffset   = 3

lLabel = 'L'

lOffset = -1
minLabel = 'MIn'
minOffset = width - 1 - font.getsize(minLabel)[0]

count = 0

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
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), 'WiFi Error', font=font, fill=orange)
    matrix.SetImage(image, 0, 0)
    time.sleep(5)

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

swap = matrix.CreateFrameCanvas()
fb = "This is my facebook message"
fbw = font.getsize(fb)[0]


while True:
    try:
        pos = width
        while pos + fbw < 0:
            swapImage = Image.new('RGB', (fbw, height))
            swapDraw  = ImageDraw.Draw(swapImage)
            swapDraw.text((0, 0), fb, font=font, fill=green)

            swap.Clear()
            swap.SetImage(image, pos, iy)
        
            pos -= 1

            time.sleep(0.1)
            swap = matrix.SwapOnVSync(swap)

        time.sleep(slideLength)
        drawClear()

        connection = urllib.urlopen('http://riotpros.com/mta/v1/?client=1')
        raw = connection.read()
        times = raw.split()
        connection.close()

        count += 1

        if count % 2:
            frame = 'ln'
        else :
            frame ='ls'

        if len(times) > 3:
            if frame == 'ln':
                min1 = times[0]
                min2 = times[1]
                dirLabel = '8 AV'
                dirOffset = 12
            if frame == 'ls':
                min1 = times[2]
                min2 = times[3]
                dirLabel = 'BKLYN'
                dirOffset = 6
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

        draw.text((lOffset, topOffset), lLabel, font=font, fill=orange)
        draw.text((fontXoffset + dirOffset, topOffset), dirLabel, font=font, fill=green)
        draw.text((time1Offset, topOffset), min1, font=font, fill=orange)
        draw.text((minOffset, topOffset), minLabel, font=font, fill=green)

        draw.text((lOffset, 16), lLabel, font=font, fill=orange)
        draw.text((fontXoffset + dirOffset, 16), dirLabel, font=font, fill=green)
        draw.text((time2Offset, 16), min2, font=font, fill=orange)
        draw.text((minOffset, 16), minLabel, font=font, fill=green)

        draw.point((width - 7, 7), fill=black)
        draw.point((width - 7, 20), fill=black)

        matrix.SetImage(image, 0, 0)

    except Exception as e:
        logging.exception("message")
        displayError()
        pass