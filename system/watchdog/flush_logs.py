import os

LOG_FILE = "/home/pi/nycts-unit/logs/logs.json"

def check_log_file():
    try:
        with open(LOG_FILE, "rb") as f:
            data = f.read()
    except Exception, e:
            remove_log_file()
    check_log_file_size()

def check_log_file_size():
    file_size = round(os.stat(LOG_FILE).st_size * .000001)
    if  file_size > 2.0:
        remove_log_file()

def remove_log_file():
    os.system("sudo rm " + LOG_FILE)
    os.system("sudo touch " + LOG_FILE)

check_log_file()
