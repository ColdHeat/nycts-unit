# encoding=utf8
import atexit
import Image
import ImageDraw
import ImageFont
import os
import time
import signal
import logging
from rgbmatrix import RGBMatrix


b = RGBMatrix(32,4)
b.brightness = 50

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

transition_time = 0.05

##### HANDLERS #####
def signal_handler(signal, frame):
    b.Clear()
    sys.exit(0)

def clearOnExit():
    b.Clear()

def drawClear():
    draw.rectangle((0, 0, width, height), fill=black)
    b.SetImage(image, 0, 0)

def displayError():
    drawClear()
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), 'WiFi Connection Error', font=font, fill=orange)
    b.SetImage(image, 0, 0)
    time.sleep(transition_time)
    drawClear()

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

swap = b.CreateFrameCanvas()


swap.Clear()
swapImage = Image.new('RGB', (width, height))
swapDraw  = ImageDraw.Draw(swapImage)
swapDraw.text((2, 0), 'NYC TRAIN SIGN'  , font=font, fill=red)
swapDraw.text((68, 0), ' legit. realtime.'  , font=font, fill=green)
swapDraw.text((2, 16), 'Loading...', font=font, fill=red)
swap.SetImage(swapImage, 0, 0)
time.sleep(transition_time)
swap = b.SwapOnVSync(swap)

try:
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
