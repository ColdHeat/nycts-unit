import os
from crontab import CronTab

cron = CronTab(user='pi')
cmd = "sudo bash /home/pi/nycts-unit/system/watchdog/wifi.sh"
cron_job = cron.new(cmd)
cron_job.minute.every(5)
cron.write()
