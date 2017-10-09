from crontab import CronTab

def remove_all_jobs():
    cron = CronTab(user='pi')
    cron.remove_all()

    write_cron_jobs()

def write_cron_jobs()
    upload_log_job()
    wifi_inspection_job()
    system_log_job()
    device_reboot_job()

def upload_log_job():
    cmd = "sudo python /home/pi/nycts-unit/system/watchdog/log.py"
    set_crontab(cmd, 25)

def wifi_inspection_job():
    cmd = "sudo python /home/pi/nycts-unit/system/watchdog/wifi.py"
    set_crontab(cmd, 5)

def system_log_job():
    cmd = "sudo python /home/pi/nycts-unit/system/watchdog/system.py"
    set_crontab(cmd, 5)

def device_reboot_job():
    cmd = "sudo python /home/pi/nycts-unit/system/watchdog/reboot.py"
    set_crontab(cmd, 3600)

def set_minute_crontab(cmd, length):
    cron = CronTab(user='pi')
    return cron.new(cmd).minute.every(length).write()
