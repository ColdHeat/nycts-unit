import time
import os
import logs
import json
from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent

class Watcher:
    FILE_TO_WATCH = "/home/pi/nycts-unit/logs/logs.json"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        print "Woof woof! <_< <_<      >_> >_>"
        event_handler = Handler()
        self.observer.schedule(event_handler, self.FILE_TO_WATCH, recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()

        self.observer.join()

class Handler(FileModifiedEvent):

    @staticmethod
    def on_any_event(event):
        fail_count = 0

        if event.event_type == 'modified':
            print "Current fail count: " + str(fail_count)

            data = []

            with open('/home/pi/nycts-unit/logs/logs.json') as f:
                for line in f:
                    data.append(json.loads(line))

            try:
                if data[-1]['status'] == 0:
                    if fail_count > 3:
                        print "Rebooting system...."
                        logs.logger.info('System Reboot', extra={'status': 1, 'job': 'system_reboot'})
                        os.system('sudo reboot now')
                    else:
                        print "Turning wifi off..."
                        os.system('sudo ifconfig wlan0 down')
                        print "Turning wifi on..."
                        os.system('sudo ifconfig wlan0 up')
                        logs.logger.info('WiFi Shutdown', extra={'status': 1, 'job': 'wifi_reboot'})
                        print "Removing tmp file..."
                        logs.logger.info('WiFi Shutdown', extra={'status': 1, 'job': 'remove_tmp_files'})
                        os.system('sudo rm -rf /home/pi/nycts-unit/tmp/*')
                        time.sleep(10)
                        fail_count += 1

            except Exception as e:
                pass


if __name__ == '__main__':
    w = Watcher()
    w.run()
