import time
import os
import logs
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    FILE_TO_WATCH = "/home/pi/nycts-unit/logs/"

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

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        fail_count = 0

        if event.event_type == 'modified':
            data = []

            with open('/home/pi/nycts-unit/logs/logs.json') as f:
                for line in f:
                    data.append(json.loads(line))

                log_status = data[-1]['status']
                if log_status == 1:
                    print "Normal Log...not doing anything"
                else:
                    if fail_count > 3:
                        logs.logger.info('System Reboot', extra={'status': 1, 'job': 'system_reboot'})
                        print "Rebooting system...."
                        os.system('sudo reboot now')
                    else:
                        logs.logger.info('WiFi Shutdown', extra={'status': 1, 'job': 'wifi_reboot'})
                        print "Turning wifi off..."
                        os.system('sudo ifconfig wlan0 down')
                        print "Turning wifi on..."
                        os.system('sudo ifconfig wlan0 up')
                        fail_count += 1
                        time.sleep(5)


if __name__ == '__main__':
    w = Watcher()
    w.run()
