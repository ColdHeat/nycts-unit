import os
from crontab import CronTab

cron = CronTab(user=True)
cron_job = cron.new(command="sudo reboot now", user='pi')
cron_job.minute.every(3)
cron_job.enable()
