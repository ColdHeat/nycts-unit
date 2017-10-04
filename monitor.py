import time
import os
import logs
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    FILE_TO_WATCH = "/home/pi/nycts-unit/logs/"
    LOG_FILE = "/home/pi/nycts-unit/logs/logs.json"

    def __init__(self):
        self.observer = Observer()
        self.state    = 'off'

    def run(self):
        print "Woof woof! <_< <_<      >_> >_> doggie Doggie!"
        event_handler = Handler()
        self.observer.schedule(event_handler, self.FILE_TO_WATCH, recursive=True)
        self.observer.start()

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
            check_internet_status()
            check_log_file()

    def check_internet_status():
        if self.state == 'demo' or 'online':
            print 'Nothing to see here...'
        elif self.state == 'offline':
            print 'The unit is offline, attempting to re-connect...'
            reboot_wifi(event)
        else:
            print 'Testing the wifi connection...'

    def check_log_file():
        last_ten_log_statuses = 0
        data = []

        try:
            with open() as f:
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

                if last_ten_log_statuses < 4:
                    print "Not enough failures"
                else:
                    reboot_system()

    def reboot_wifi():
        logs.logger.info('WiFi Shutdown', extra={'status': 1, 'job': 'wifi_reboot'})
        print "Turning wifi off..."
        os.system("sudo /sbin/ifdown 'wlan0' && sleep 5")
        print "Turning wifi on..."
        os.system("sudo /sbin/ifup --force 'wlan0'")
        print "Waiting for the wifi to re-connect..."
        self.state = 'connecting'

    def check_internet_status():
        print "Checking internet status"

    def reboot_system():
        logs.logger.info('System Reboot', extra={'status': 1, 'job': 'system_reboot'})
        print "Rebooting system...."
        os.system('sudo reboot now')

if __name__ == '__main__':
    w = Watcher()
    w.run()
