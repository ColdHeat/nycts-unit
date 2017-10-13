import time
import os
import logs
import json
import urllib2
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    LOG_FILE = "/home/pi/nycts-unit/logs/"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        print "Loading Watchdog..."
        event_handler = Handler()
        self.observer.schedule(event_handler, self.LOG_FILE, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()

    def get_system_state(self):
        try:
            result = urllib2.urlopen(
                "http://127.0.0.1:3000/getConfig"
            )
            return json.loads(result.read())
        except urllib2.URLError as e:
            logs.logger.info(
                'API Config Retrival',
                    extra={'status': 0, 'job': 'api_config', 'error': str(e)})

    def go_online(self):
        try:
            result = urllib2.urlopen(
                "http://127.0.0.1:3000/setConfig/settings/state/online")
        except urllib2.URLError as e:
            logs.logger.info(
                'API Reboot',
                    extra={'status': 0, 'job': 'api_reboot', 'error': str(e)})

    def go_offline(self):
        try:
            result = urllib2.urlopen(
                "http://127.0.0.1:3000/setConfig/settings/state/offline")
        except urllib2.URLError as e:
            logs.logger.info(
                'API Reboot',
                    extra={'status': 0, 'job': 'api_reboot', 'error': str(e)})

    def set_reboot(self):
        try:
            result = urllib2.urlopen(
                "http://127.0.0.1:3000/setConfig/settings/reboot/false")
        except urllib2.URLError as e:
            logs.logger.info(
                'API Reboot',
                    extra={'status': 0, 'job': 'api_reboot', 'error': str(e)})

    def check_log_file(self):
        data = []

        try:
            with open("/home/pi/nycts-unit/logs/logs.json") as f:
                for line in f:
                    data.append(json.loads(line))
        except Exception, e:
            os.system("sudo rm /home/pi/nycts-unit/logs/logs.json")
            os.system("sudo touch /home/pi/nycts-unit/logs/logs.json")
            data.append({})

        sum_log_status_codes(data)

    def sum_log_status_codes(self, data):
        last_ten_log_statuses = 0

        if len(data) > 10:
            for log in data[-10:]:
                status_code = log['status']
                last_ten_log_statuses += status_code

            if last_ten_log_statuses < 1:
                w.go_offline()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.event_type == 'modified':
            state = w.get_system_state()['settings']['state']

            if state == 'online':
                w.check_log_file()
            else:
                w.set_reboot()


if __name__ == '__main__':
    w = Watcher()
    w.run()
