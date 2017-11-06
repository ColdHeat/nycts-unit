import os
from crontab import CronTab

CHANGE_DIR = "cd /home/pi/nycts-unit"

def initialize_crontab():
    os.system("sudo -u pi crontab -r")
    write_cron_jobs()

def write_cron_jobs():
    upload_log_job()
    wifi_inspection_job()
    system_log_job()
    device_reboot_job()
    flush_logs()

def upload_log_job():
    cmd = CHANGE_DIR + " && sudo python system/watchdog/log.py"
    set_crontab(cmd, 25)

def wifi_inspection_job():
    cmd = CHANGE_DIR + " && sudo python system/watchdog/wifi.py"
    set_crontab(cmd, 1)

def system_log_job():
    cmd = CHANGE_DIR + " && sudo python system/watchdog/system.py"
    set_crontab(cmd, 2)

def device_reboot_job():
    cmd = CHANGE_DIR + " && sudo python system/watchdog/reboot.py"
    set_crontab(cmd, 1)

def flush_logs():
    cmd = CHANGE_DIR + " && sudo python system/watchdog/flush_logs.py"
    set_crontab(cmd, 86400)

def set_crontab(cmd, length):
    cron = CronTab(user='pi')
    cron.new(cmd).minute.every(length)
    cron.write()

initialize_crontab()
