# encoding=utf8
import atexit
import Image
import ImageDraw
import ImageFont
import os
import time
import signal
import logging
import constants
from rgbmatrix import RGBMatrix, RGBMatrixOptions

options = RGBMatrixOptions()
options.gpio_slowdown = 2
options.pwm_bits = 10
options.hardware_mapping = 'adafruit-hat-pwm'
b = RGBMatrix(32,4, options = options)
b.brightness = 60
direction = True
fontXoffset = 0
topOffset   = 3

##### HANDLERS #####
def signal_handler(signal, frame):
    b.Clear()
    sys.exit(0)

def clearOnExit():
    b.Clear()

def drawClear():
    draw.rectangle((0, 0, constants.width, constants.height), fill=constants.black)
    b.SetImage(image, 0, 0)

def displayError():
    drawClear()
    draw.text((0 + fontXoffset + 3, 0 + topOffset + 0), 'WiFi Connection Error', font=constants.font, fill=constants.orange)
    b.SetImage(image, 0, 0)
    time.sleep(transition_time)
    drawClear()

atexit.register(clearOnExit)
signal.signal(signal.SIGINT, signal_handler)

swap = b.CreateFrameCanvas()

swap.Clear()
swapImage = Image.new('RGB', (constants.width, constants.height))
swapDraw  = ImageDraw.Draw(swapImage)
swapDraw.text((2, 0), 'NYC TRAIN SIGN'  , font=constants.font, fill=constants.red)
swapDraw.text((68, 0), ' legit. realtime.'  , font=constants.font, fill=constants.green)
swapDraw.text((2, 16), 'Loading...', font=constants.font, fill=constants.red)
swap.SetImage(swapImage, 0, 0)
swap = b.SwapOnVSync(swap)

try:
    while True:
        if b.brightness == 60:
            direction = False
        if b.brightness == 30:
            direction = True

        if direction == True:
            b.brightness += 1
        else:
            b.brightness -= 1
        swap.Clear()
        swap.SetImage(swapImage, 0, 0)
        swap = b.SwapOnVSync(swap)
        time.sleep(0.02)
except KeyboardInterrupt:
    sys.exit(0)
