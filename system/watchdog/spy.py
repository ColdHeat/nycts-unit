import os
import os.path
import time
import json
import socket
import urllib2

def load_config_file():
    baseurl = "http://127.0.0.1:3000/getConfig"
    try:
        result = urllib2.urlopen(baseurl)
    except urllib2.URLError as e:
        print "Can't load config file..."
    config = json.loads(result.read())
    return config

def check_hostname():
    hostname = socket.gethostname()
    sign_id = "nycts-" + load_config_file()['settings']['sign_id']

    if hostname == sign_id:
        check_dataplicity_install()
    else:
        change_hostname(sign_id)

def change_hostname(sign_id):
    os.system("sudo hostnamectl set-hostname " + sign_id)
    check_dataplicity_install()

def check_dataplicity_install():
    dataplicity_is_installed = os.path.exists("/opt/dataplicity/tuxtunnel/auth")

    if dataplicity_is_installed:
        pass
    else:
        install_dataplicity()

def install_dataplicity():
    while True:
        if os.system("ping -c 1 google.com") == 0:
            try:
                os.system("sudo python /home/pi/nycts-unit/system/install/dataplicity.py")
                set_reboot_to_true()
            except:
                print "Failed to install dataplicity..."
                pass
        time.sleep(2)

def set_reboot_to_true():
    try:
        result = urllib2.urlopen("http://127.0.0.1:3000/setConfig/settings/reboot/true")
    except urllib2.URLError as e:
        print 'Something went wrong setting reboot to true...'

check_hostname()
