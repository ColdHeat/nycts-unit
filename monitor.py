import time
import os
import logs
import json
import urllib2
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    FILE_TO_WATCH = "/home/pi/nycts-unit/logs/"
    LOG_FILE = "/home/pi/nycts-unit/logs/logs.json"

    def __init__(self):
        self.observer = Observer()
        self.state    = self.get_state()

    def run(self):
        print "Woof woof! <_< <_<      >_> >_> doggie Doggie!"
        event_handler = Handler()
        self.observer.schedule(event_handler, self.FILE_TO_WATCH, recursive=True)
        self.observer.start()

    def get_state(self):
        baseurl = "http://127.0.0.1:3000/getConfig"
        try:
            result = urllib2.urlopen(baseurl)
        except urllib2.URLError as e:
            logs.logger.info('API Config', extra={'status': 0, 'job': 'api_config'}, exc_info=True)
        else:
            config = json.loads(result.read())
        return config['settings']['state']

        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()

        self.observer.join()

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.event_type == 'modified':
            if self.state == 'demo' or 'online':
                last_ten_log_statuses = 0
                data = []

                try:
                    with open(LOG_FILE) as f:
                        for line in f:
                            data.append(json.loads(line))
                except:
                    os.system("sudo rm" + LOG_FILE)
                    os.system("sudo touch" + LOG_FILE)

                    if len(data) < 10:
                        print "Not enough logs to make a move"
                    else:
                        for log in data[-10:]:
                            status_code = log['status']
                            last_ten_log_statuses += status_code

                        if last_ten_log_statuses > 4:
                            logs.logger.info('System Reboot', extra={'status': 1, 'job': 'system_reboot'})
                            print "Rebooting system...."
                            os.system('sudo reboot now')

            elif self.state == 'offline':
                print 'The unit is offline, attempting to re-connect...'
                logs.logger.info('WiFi Shutdown', extra={'status': 1, 'job': 'wifi_reboot'})
                print "Turning wifi off..."
                os.system("sudo /sbin/ifdown 'wlan0' && sleep 5")
                print "Turning wifi on..."
                os.system("sudo /sbin/ifup --force 'wlan0'")
                print "Waiting for the wifi to re-connect..."
                self.state = 'connecting'

            else:
                print 'Testing the wifi connection...'


if __name__ == '__main__':
    w = Watcher()
    w.run()
