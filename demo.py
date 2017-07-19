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
width          = 128
height         = 32

matrix                   = RGBMatrix(32, 4) # rows, chain length
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

dat = {}
dat[0] = {}
dat[1] = {}
while True:

    lLabel = 'L '
    topOffset = 3
    lOffset = 4
    minLabel = 'MIn'
    minOffset = width - 6 - font.getsize(minLabel)[0]


    min1 = '2'
    min2 = '13'
    dirLabel1 = '   BROOKLN '
    dirOffset1 = 22

    dirLabel2 = '   MANHATTAN '
    dirOffset2 = 22

    if len(min1) < 2:
        min1 = min1.rjust(3)
    time1Offset = minOffset - font.getsize(min1)[0]

    if len(min2) < 2:
        min2 = min2.rjust(3)
    time2Offset = minOffset - font.getsize(min2)[0]

    draw.text((lOffset, 0 + topOffset), lLabel, font=font, fill=orange)
    draw.text((fontXoffset + dirOffset1, 0 + topOffset), dirLabel1, font=font, fill=green)
    draw.text((time1Offset, 0 + topOffset), min1, font=font, fill=orange)
    draw.text((minOffset, 0 + topOffset), minLabel, font=font, fill=green)

    draw.text((lOffset, 16), lLabel, font=font, fill=orange)
    draw.text((fontXoffset + dirOffset2, 16), dirLabel2, font=font, fill=green)
    draw.text((time2Offset, 16), min2, font=font, fill=orange)
    draw.text((minOffset, 16), minLabel, font=font, fill=green)

    draw.point((width - 12, 7), fill=black)
    draw.point((width - 12, 20), fill=black)

    matrix.SetImage(image, 0, 0)
    time.sleep(slideLength)
    drawClear()

    dat[0]['min'] = '4'
    dat[0]['term'] = 'Brooklyn Bridge '
    dat[0]['line'] = '6'
    dat[0]['col'] = green

    dat[1]['min'] = '11'
    dat[1]['term'] = 'South Ferry '
    dat[1]['line'] = '1'
    dat[1]['col'] = red

    for row in [0, 1]:

        data = dat[row]

        xOff = 2
        yOff = 2
        
        mins = str(data['min'])
        if len(mins) < 2:
            mins = mins.rjust(3)

        minLabel = mins + 'mIn'
        dirLabel = '  ' + data['term']

        nums = data['line']
        ccol = data['col']
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
        draw.ellipse((circleXoffset, circleYoffset, circleXend, circleYend), fill=ccol)
        draw.text((circleXoffset + 1, circleYoffset - 2), nums, font=font, fill=black)
        draw.text((circleXend, fontYoffset), dirLabel, font=font, fill=green)
        draw.text((minPos, fontYoffset), minLabel, font=font, fill=green)

        draw.point((width - 9, 5), fill=black)
        draw.point((width - 9, 7), fill=black)
        draw.point((width - 9, 21), fill=black)
        draw.point((width - 9, 23), fill=black)

    matrix.SetImage(image, 0, 0)
    time.sleep(slideLength)
    drawClear()
