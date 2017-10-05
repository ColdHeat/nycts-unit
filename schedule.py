import os
from crontab import CronTab

cron = CronTab(user='pi')
cmd = "sudo reboot now"
cron_job = cron.new(cmd)
cron_job.minute.every(1)
cron.write()
print cron.render()
