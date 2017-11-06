import os
import sys

os.system("sudo pkill -f load.py")
os.system("sudo python /home/pi/nycts-unit/readytopair.py &")
sys.exit()
