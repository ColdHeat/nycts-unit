import os
from crontab import CronTab

cron = CronTab(user=True)
cron_job = cron.new(command="sudo /sbin/ifdown 'wlan0'", user='pi')
cron_job.minute.every(1)
cron_job.enable()
