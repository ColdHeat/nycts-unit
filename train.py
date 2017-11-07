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
from transit import mta
from transit import bart

class train:

    def __init__(self, base):
        self.base = base
        self.config = base.config
        self.start = time.time()
        self.train_data = self.offline_train_data()
        self.train_directions = ['N', 'S']
        t = threading.Thread(target=self.thread)
        t.daemon = True
        t.start()

    def offline_train_data(self):
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
                self.config = self.base.config
                url = self.config['subway']['service']['endpoint-times'] + self.config['subway']['train']
                print url
                try:
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
                            route[0]['arrivalTime'] = route[1]['arrivalTime']
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
        if self.config['subway']['service']['key'] == "MTA":
            mta.draw(direction, constants, self.config, self.train_data, self.train_directions, self.base.matrix)
        if self.config['subway']['service']['key'] == "BART":
            bart.draw(direction, constants, self.config, self.train_data, self.train_directions, self.base.matrix)
        time.sleep(self.base.getTransitionTime())
