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
import requests
import random
import os

class train:

    def __init__(self, base):
        self.base = base
        self.config = base.config
        self.start = time.time()
        self.train_data = self.offline_train_data()
        self.train_directions = []
        t = threading.Thread(target=self.thread)
        t.daemon = True
        t.start()

    def offline_train_data(self):
        self.train_directions = ['N', 'S']
        train_line = self.config["subway"]["line"]
        with open('./offline_data/'+ train_line + '.json') as json_file:
            json_data = json.load(json_file)
        return json_data["data"]

    def thread(self):
        while True:
            def check_device_state():
                if self.config['settings']['state'] == 'online':
                    request_train_time()
                else:
                    calculate_time_difference()

            def request_train_time():
                try:
                    url = \
                        'https://api.trainsignapi.com/prod-trains/stations/' \
                        + self.config['subway']['train']
                    querystring = {'': ''}
                    headers = {
                        'x-api-key': self.config['settings']['prod_api_key']
                        }
                    response = requests.request(
                        'GET', url, headers=headers, params=querystring)

                    validate_train_data(json.loads(response.text)['data'])

                except Exception, e:
                    self.train_data = self.offline_train_data()

                    logs.logger.info(
                        'Train module', extra={
                            'status': 0,
                            'job': 'train_module',
                            'error': str(e)
                            })

            def validate_train_data(response_data):
                north_bound = self.train_data['N']['schedule']
                south_bound = self.train_data['S']['schedule']

                is_first_stop = len(south_bound) == 0
                is_last_stop = len(north_bound) == 0

                if is_first_stop and is_last_stop:
                    self.train_directions = ['N', 'S']
                    self.train_data = self.offline_train_data()
                elif is_first_stop:
                    self.train_directions = ['N']
                    self.train_data = response_data
                    self.train_data['N']['term'] = self.train_data['S']['term']
                elif is_last_stop:
                    self.train_directions = ['S']
                    self.train_data = response_data
                    self.train_data['S']['term'] = self.train_data['N']['term']
                else:
                    self.train_directions = ['N', 'S']
                    self.train_data = response_data

            def calculate_time_difference():
                time_difference = math.ceil(time.time() - self.start)

                if time_difference >= 60:
                    self.start = time.time()
                    update_offline_train_data()

            def update_offline_train_data():
                for direction in self.train_directions:
                    route = self.train_data[direction]['schedule']

                    for row in range(len(route)):
                        arrival_less_than_zero = route[row]['arrivalTime'] <= 0

                        if row == 0 and arrival_less_than_zero:
                            route[0]['arrivalTime'] = train[1]['arrivalTime']
                            route[1]['arrivalTime'] += random.choice([4, 6, 8])
                        if row == 1 and arrival_less_than_zero:
                            route[0]['arrivalTime'] -= 1
                            route[1]['arrivalTime'] = random.choice([7, 9, 11])
                        route[row]['arrivalTime'] -= 1

            time.sleep(5)
            check_device_state()

    def drawClear(self):
        image = Image.new('RGB', (constants.width, constants.height))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, constants.width, constants.height),
            fill=constants.black)
        self.base.matrix.SetImage(image, 0, 0)

    def draw(self, direction):
        self.config = self.base.config
        image = Image.new('RGB', (constants.width, constants.height))
        draw = ImageDraw.Draw(image)
        customer_retention = self.config['settings']['customer_retention']
        schedule_length = range(len(self.train_data[direction]['schedule']))

        if direction in self.train_directions:
            if customer_retention == True:
                index_range = schedule_length[1:3:]
            else:
                index_range = schedule_length[0:2:]

            for row in index_range:
                self.data = self.train_data[direction]['schedule'][row]
                xOff = 2
                yOff = 2

                mins = str(self.data['arrivalTime'])
                if len(mins) < 2:
                    mins = mins.rjust(3)

                minLabel = 'Min'
                dirLabel = '  ' + self.train_data[direction]['term']

                nums = self.data['routeId']

                if nums in ['1', '2', '3']:
                    circleColor = constants.red
                if nums in ['4', '5', '6', 'G']:
                    circleColor = constants.green
                if nums in ['N', 'Q', 'R', 'W']:
                    circleColor = constants.yellow
                if nums in ['B', 'D', 'F', 'M']:
                    circleColor = constants.orange
                if nums in ['L']:
                    circleColor = constants.grey

                if row == 1:
                    yOff = 18

                fontXoffset = xOff
                fontYoffset = yOff

                numLabel = str(row + 1) + '. '
                numLabelW = constants.font.getsize(numLabel)[0]

                minPos = constants.width \
                    - constants.font.getsize(minLabel)[0] - 3

                circleXoffset = fontXoffset + numLabelW - 6
                circleYoffset = yOff + 1

                circleXend = circleXoffset + 8
                circleYend = circleYoffset + 8

                minOffset = constants.width - 6 \
                    - constants.font.getsize(minLabel)[0]
                timeOffset = minOffset - constants.font.getsize(mins)[0]
                draw.ellipse((circleXoffset, circleYoffset, circleXend,
                    circleYend), fill=circleColor)
                draw.text((circleXoffset + 1, circleYoffset - 2), nums,
                    font=constants.font, fill=constants.black)
                draw.text((circleXend, fontYoffset), dirLabel,
                    font=constants.font, fill=constants.green)
                draw.text((timeOffset, 0 + fontYoffset), mins,
                    font=constants.font, fill=constants.orange)
                draw.text((minOffset, 0 + fontYoffset), minLabel,
                    font=constants.font, fill=constants.green)


            self.base.matrix.SetImage(image, 0, 0)
            time.sleep(self.base.getTransitionTime())
