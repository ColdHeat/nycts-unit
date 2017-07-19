# NextBus scrolling marquee display for Adafruit RGB LED matrix (64x32).
# Requires rgbmatrix.so library: github.com/adafruit/rpi-rgb-led-matrix

import logging
import atexit
import Image
import ImageDraw
import ImageFont
import math
import os
import time
import urllib
from rgbmatrix import RGBMatrix

# Configurable stuff ---------------------------------------------------------

width          = 128  # Matrix size (pixels) -- change for different matrix
height         = 32  # types (incl. tiling).  Other code may need tweaks.
matrix         = RGBMatrix(32, 4) # rows, chain length
matrix.brightness = 20
matrix.pwmBits = 3
matrix.luminanceCorrect = False

routeColor     = (255, 255, 255) # Color for route labels (usu. numbers)
descColor      = (110, 110, 110) # " for route direction/description
longTimeColor  = (  0, 255,   0) # Ample arrival time = green
midTimeColor   = (255, 255,   0) # Medium arrival time = yellow
shortTimeColor = (255,   0,   0) # Short arrival time = red
minsColor      = (110, 110, 110) # Commans and 'minutes' labels
noTimesColor   = (  0,   0, 255) # No predictions = blue

orangeColor    = (255, 100, 0)
greenColor     = (0,   255, 0)
# TrueType fonts are a bit too much for the Pi to handle -- slow updates and
# it's hard to get them looking good at small sizes.  A small bitmap version
# of Helvetica Regular taken from X11R6 standard distribution works well:
font           = ImageFont.load(os.path.dirname(os.path.realpath(__file__))
                   + '/helvR08.pil')
fontYoffset    = -2  # Scoot up a couple lines so descenders aren't cropped
fontXoffset    = 0

topOffset = 3

# Main application -----------------------------------------------------------

# Drawing takes place in offscreen buffer to prevent flicker
image       = Image.new('RGB', (width, height))
draw        = ImageDraw.Draw(image)
currentTime = 0.0
prevTime    = 0.0
x = 1
y = 10
# Clear matrix on exit.  Otherwise it's annoying if you need to break and
# fiddle with some code while LEDs are blinding you.
def clearOnExit():
    matrix.Clear()

atexit.register(clearOnExit)

label = 'L MANHATTAN 10 MIN'
w = font.getsize(label)[0]

lLabel = 'L '

lOffset = 4
minLabel = 'Min'
minOffset = width - 6 - font.getsize(minLabel)[0]

count = 0
#draw.rectangle((0, 0, 10, 10), fill=(255, 0, 0))
#draw.rectangle((10, 10, 10, 10), fill=(0, 255, 0))

while True:
    try:

        connection = urllib.urlopen('http://riotpros.com/mta/mta/l2.php')
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
            time1Offset = minOffset - font.getsize(min1)[0] - 1

        if len(min2) < 2:
            min2 = min2.rjust(3)
            time2Offset = minOffset - font.getsize(min2)[0] - 1

        lLabelw = font.getsize(lLabel)[0]

        dirLabelw = font.getsize(dirLabel)[0]

        draw.text((lOffset, 0 + topOffset), lLabel, font=font, fill=orangeColor)
        draw.text((fontXoffset + dirOffset, 0 + topOffset), dirLabel, font=font, fill=greenColor)
        draw.text((time1Offset, 0 + topOffset), min1, font=font, fill=orangeColor)
        draw.text((minOffset, 0 + topOffset), minLabel, font=font, fill=greenColor)

        draw.text((lOffset, 16), lLabel, font=font, fill=orangeColor)
        draw.text((fontXoffset + dirOffset, 16), dirLabel, font=font, fill=greenColor)
        draw.text((time2Offset, 16), min2, font=font, fill=orangeColor)
        draw.text((minOffset, 16), minLabel, font=font, fill=greenColor)

        matrix.SetImage(image, 0, 0)
        time.sleep(7)
        if frame == 'ls':
            draw.text((48 + fontXoffset, 0 + topOffset), minLabel, font=font, fill=(0, 0, 0))
            draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
            matrix.SetImage(image, 0, 0)

            draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), 'Photo Contest: FREE Sign!', font=font, fill=orangeColor)
            draw.text((0 + fontXoffset + 3, 0 + topOffset + 16), 'Like @NycTrainSign For Perks', font=font, fill=orangeColor)
            matrix.SetImage(image, 0, 0)
            time.sleep(3)

        draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
        matrix.SetImage(image, 0, 0)
    except:
        draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), 'WiFi Connection Error', font=font, fill=orangeColor)
        draw.text((0 + fontXoffset + 3, 0 + topOffset + 16), 'Like @NycTrainSign For Perks', font=font, fill=orangeColor)
        matrix.SetImage(image, 0, 0)
        time.sleep(5)
        draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
        matrix.SetImage(image, 0, 0)
        pass
