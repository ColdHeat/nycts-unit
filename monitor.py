import time
import os
import logs
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    DIRECTORY_TO_WATCH = "/home/pi/nycts-unit/tmp/"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        print "Woof woof! <_< <_<      >_> >_>"
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print "Error"

        self.observer.join()

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        fail_count = 0

        if event.is_directory:
            return None

        elif event.event_type == 'created':
            print "Received created event - %s." % event.src_path
            print "Current fail count: " + str(fail_count)

            if fail_count > 3:
                print "Rebooting system...."
                logs.logger.info('System Reboot', extra={'status': 1, 'job': 'system_reboot'})
                os.system('sudo reboot now')
            else:
                print "Turning wifi off..."
                os.system('sudo ifconfig wlan0 down')
                print "Turning wifi on..."
                os.system('sudo ifconfig wlan0 up')
                # os.system("sudo python /home/pi/nycts-unit/system/test.py")
                logs.logger.info('WiFi Shutdown', extra={'status': 1, 'job': 'wifi_reboot'})
                print "Removing tmp file..."
                logs.logger.info('WiFi Shutdown', extra={'status': 1, 'job': 'remove_tmp_files'})
                os.system('sudo rm -rf /home/pi/nycts-unit/tmp/*')
                time.sleep(10)
                fail_count += 1

if __name__ == '__main__':
    w = Watcher()
    w.run()
