import threading
import time
import urllib
import json
import urllib2
import Image
import ImageDraw
import constants
import math


class train:

    def __init__(self, base):
        self.base          = base
        self.config        = base.config
        self.start         = time.time()

        self.train_data    = {"N":[{"line":"R","min":6,"term":"Queens "},{"line":"N","min":7,"term":"Astoria "}],"S":[{"line":"R","min":2,"term":"Whitehall "},{"line":"N","min":6,"term":"Coney Island "}]}
        t                  = threading.Thread(target=self.thread)
        t.daemon           = True
        t.start()

    # Periodically get predictions from server ---------------------------
    def thread(self):
        while True:
            try:
                connection = urllib2.urlopen('http://riotpros.com/mta/v1/combo.php?client=' + self.config["settings"]["client_id"])
                # logger.info('Train Screen', extra={'status': 1, 'job': 'train_screen'})
                raw = connection.read()
                parsed = json.loads(raw)
                connection.close()
                self.train_data = parsed
            except Exception as e:

                end = time.time()

                time_difference = math.ceil(end - self.start)

                if time_difference >= 60:
                    self.start = time.time()
                    end = time.time()

                parsed = self.train_data

                if len(mins) < 3:
                    if self.data['min'] <= 0:
                        mins = str((int(self.data['min']) + 6))
                        self.data['min'] = int(mins)
                    else:
                        mins = str((int(self.data['min']) - int(time_difference)/ 60))
                        self.data['min'] = int(mins)

                error_message = e.reason
                #logger.info('Train Screen', extra={'status': 0, 'job': 'train_screen', 'error': error_message})

            time.sleep(5)
    def drawClear(self):
        image     = Image.new('RGB', (constants.width, constants.height))
        draw      = ImageDraw.Draw(image)
        draw.rectangle((0, 0, constants.width, constants.height), fill=constants.black)
        self.base.matrix.SetImage(image, 0, 0)

    def draw(self, direction):
        image     = Image.new('RGB', (constants.width, constants.height))
        draw      = ImageDraw.Draw(image)

        for row in [0, 1]:
            self.data = self.train_data[direction][row]
            xOff = 2
            yOff = 2

            mins = str(self.data['min'])
            if len(mins) < 2:
                mins = mins.rjust(3)

            minLabel = 'mIn'
            dirLabel = '  ' + self.data['term']

            nums = self.data['line']

            if nums in ['1', '2', '3']:
                circleColor = constants.red
            if nums in ['4', '5', '6']:
                circleColor = constants.green
            if nums in ['N', 'Q', 'R', 'W']:
                circleColor = constants.yellow
            if nums in ['L']:
                circleColor = constants.grey

            if row == 1:
                yOff = 18

            fontXoffset = xOff
            fontYoffset = yOff

            numLabel = str(row + 1) + '. '
            numLabelW = constants.font.getsize(numLabel)[0]

            minPos = constants.width - constants.font.getsize(minLabel)[0] - 3

            circleXoffset = fontXoffset + numLabelW
            circleYoffset = yOff + 1;

            circleXend = circleXoffset + 8
            circleYend = circleYoffset + 8

            #if self.data['line'] == 'L':
            #    dirOffset = 26
            #    lLabel = 'L '
            #    minLabel = 'MIn'
            #    lOffset = 4
            #    minOffset = constants.width - 6 - constants.font.getsize(minLabel)[0]
            #    timeOffset = minOffset - constants.font.getsize(mins)[0]

            #    draw.text((lOffset, 0 + fontYoffset), lLabel, font=constants.font, fill=constants.orange)
            #    draw.text((fontXoffset + dirOffset, 0 + fontYoffset), dirLabel, font=constants.font, fill=constants.green)

            #    draw.text((timeOffset, 0 + fontYoffset), mins, font=constants.font, fill=constants.orange)
            #    draw.text((minOffset, 0 + fontYoffset), minLabel, font=constants.font, fill=constants.green)

            #    draw.point((constants.width - 12, 6), fill=constants.black)
            #    draw.point((constants.width - 12, 22), fill=constants.black)

            #else:
            minOffset = constants.width - 6 - constants.font.getsize(minLabel)[0]
            timeOffset = minOffset - constants.font.getsize(mins)[0]
            #draw.text((fontXoffset, fontYoffset), numLabel, font=constants.font, fill=constants.green)
            draw.ellipse((circleXoffset, circleYoffset, circleXend, circleYend), fill=circleColor)
            draw.text((circleXoffset + 1, circleYoffset - 2), nums, font=constants.font, fill=constants.black)
            draw.text((circleXend, fontYoffset), dirLabel, font=constants.font, fill=constants.green)
            draw.text((timeOffset, 0 + fontYoffset), mins, font=constants.font, fill=constants.orange)
            draw.text((minOffset, 0 + fontYoffset), minLabel, font=constants.font, fill=constants.green)

            draw.point((constants.width - 9, 6), fill=constants.black)
            draw.point((constants.width - 9, 22), fill=constants.black)

        self.base.matrix.SetImage(image, 0, 0)
        time.sleep(self.base.getTransitionTime())
