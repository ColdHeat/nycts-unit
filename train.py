import threading
import time
import urllib
import json
import urllib2
import Image
import ImageDraw
import constants
import math
import logs

class train:

    def __init__(self, base):
        self.base          = base
        self.config        = base.config
        self.start         = time.time()
        self.train_data    = {
        	"data": {
        		"N": {
        			"schedule": [
        				{
        					"routeId": "G",
        					"delay": null,
        					"arrivalTime": 5,
        					"departureTime": 1505320882
        				},
        				{
        					"routeId": "G",
        					"delay": null,
        					"arrivalTime": 10,
        					"departureTime": 1505321185
        				}
        			],
        			"term": "QUEENS"
        		},
        		"S": {
        			"schedule": [
        				{
        					"routeId": "G",
        					"delay": null,
        					"arrivalTime": 5,
        					"departureTime": 1505320882
        				},
        				{
        					"routeId": "G",
        					"delay": null,
        					"arrivalTime": 14,
        					"departureTime": 1505321400
        				}
        			],
        			"term": "BROOKLYN"
        		}
        	}
        }
        t                  = threading.Thread(target=self.thread)
        t.daemon           = True
        t.start()

    def thread(self):
        while True:
            try:
                url = "https://api.trainsignapi.com/dev-trains/stations/" + self.config["subway"]["train"]
                querystring = {"":""}
                headers = {'x-api-key': self.config["settings"]["dev_api_key"]}

                response = requests.request("GET", url, headers=headers, params=querystring)
                data = json.loads(response.text)

                print data

                self.train_data["state"] = "live"
                self.train_data = data
            except Exception as e:
                error_message = e.reason
                print error_message
                # logs.logger.info('Train module', extra={'status': 0, 'job': 'train_module', })
                # end = time.time()
                #
                # time_difference = math.ceil(end - self.start)
                #
                # if time_difference >= 60:
                #     self.start = time.time()
                #     end = time.time()
                #
                # if len(mins) < 3:
                #     if self.data['arrivalTime'] <= 0:
                #         mins = str((int(self.data['arrivalTime']) + 6))
                #         self.data['arrivalTime'] = int(mins)
                #     else:
                #         mins = str((int(self.data['arrivalTime']) - int(time_difference)/ 60))
                #         self.data['arrivalTime'] = int(mins)
                # error_message = e.reason

            # time.sleep(5)

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

            mins = str(self.data['schedule']['arrivalTime'])
            if len(mins) < 2:
                mins = mins.rjust(3)

            minLabel = 'mIn'
            dirLabel = '  ' + self.data['term']

            nums = self.data['line']

            if nums in ['1', '2', '3']:
                circleColor = constants.red
            if nums in ['4', '5', '6', 'G']:
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

            minOffset = constants.width - 6 - constants.font.getsize(minLabel)[0]
            timeOffset = minOffset - constants.font.getsize(mins)[0]
            draw.ellipse((circleXoffset, circleYoffset, circleXend, circleYend), fill=circleColor)
            draw.text((circleXoffset + 1, circleYoffset - 2), nums, font=constants.font, fill=constants.black)
            draw.text((circleXend, fontYoffset), dirLabel, font=constants.font, fill=constants.green)
            draw.text((timeOffset, 0 + fontYoffset), mins, font=constants.font, fill=constants.orange)
            draw.text((minOffset, 0 + fontYoffset), minLabel, font=constants.font, fill=constants.green)

            draw.point((constants.width - 9, 6), fill=constants.black)
            draw.point((constants.width - 9, 22), fill=constants.black)

        self.base.matrix.SetImage(image, 0, 0)
        time.sleep(self.base.getTransitionTime())
