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
topOffset   = 3

lLabel = 'L '

lOffset = 4
minLabel = 'MIn'
minOffset = width - 6 - font.getsize(minLabel)[0]

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
    drawClear()
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), 'WiFi Connection Error', font=font, fill=orange)
    matrix.SetImage(image, 0, 0)
    time.sleep(5)
    drawClear()

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

swap = matrix.CreateFrameCanvas()

while True:
    try:

        time.sleep(slideLength)
        drawClear()

        count += 1

        if count % 2:
            frame = 'ln'
        else :
            frame ='ls'

        if True:
        #if count % 10 =- 0:
            try:
                connection = urllib.urlopen('http://riotpros.com/mta/fb/fathers.php')
                raw = connection.read()
                connection.close()

                parsed = json.loads(raw)
                msg = parsed['msg']
                date = parsed['date']
                fbw = font.getsize(msg)[0]
                fbiw = width
                if fbw < width:
                    fbiw = fbw

                pos = width

                while pos + fbw > 0:
                    swapImage = Image.new('RGB', (fbiw, height))
                    swapDraw  = ImageDraw.Draw(swapImage)
            
                    swapDraw.text((5, 0), date , font=font, fill=red)
                    swapDraw.text((35, 0), '@' , font=font, fill=green)
                    swapDraw.text((43, 0), 'FATHERSBK' , font=font, fill=orange)
                    swapDraw.text((pos, 16), msg, font=font, fill=green)

                    swap.Clear()
                    swap.SetImage(swapImage, 0, 0)
                
                    pos -= 1

                    time.sleep(0.05)
                    swap = matrix.SwapOnVSync(swap)
                
                swap.Clear()
                swapImage = Image.new('RGB', (width, height))
                swapDraw  = ImageDraw.Draw(swapImage)
                swapDraw.text((5, 0), 'NYCTRAINSIGN.COM' , font=font, fill=red)
                swapDraw.text((5, 16), '@' , font=font, fill=green)
                swapDraw.text((15, 16), 'NYCTRAINSIGN' , font=font, fill=orange)
                swap.SetImage(swapImage, 0, 0)
                swap = matrix.SwapOnVSync(swap)
                time.sleep(5)

            except Exception as e:
                logging.exception("message")
                pass
            

        connection = urllib.urlopen('http://riotpros.com/mta/v1/?client=5')
        raw = connection.read()
        times = raw.split()
        connection.close()

        if len(times) > 3:
            if frame == 'ln':
                min1 = times[0]
                min2 = times[1]
                dirLabel = '    MANHATTAN '
                dirOffset = 22
            if frame == 'ls':
                min1 = times[2]
                min2 = times[3]
                dirLabel = '   ROCKAWAY PKWY'
                dirOffset = 12
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
        swap = matrix.SwapOnVSync(swap)

    except Exception as e:
        logging.exception("message")
        displayError()
        pass