import os
from crontab import CronTab

cron = CronTab(user='pi')
cmd = "sudo reboot now"
cron_job = tab.new(cmd)
cron_job.minute.every(1)
cron_job.write()
print cron_job.render()
