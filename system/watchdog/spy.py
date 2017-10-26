import os
import os.path
import json
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
    hostname = os.system("hostname")
    sign_id = load_config_file()['settings']['sign_id']

    if hostname == sign_id:
        check_dataplicity_install()
    else:
        change_hostname(sign_id)

def change_hostname(sign_id):
    os.system("sudo hostnamectl set-hostname " + sign_id)
    set_reboot_to_true()
    check_dataplicity_install()

def set_reboot_to_true():
    try:
        result = urllib2.urlopen(
            "http://127.0.0.1:3000/setConfig/settings/reboot/true")
    except urllib2.URLError as e:
        print 'Something went wrong setting reboot to true...'

def check_dataplicity_install():
    dataplicity_is_installed = os.path.exists("/var/log/dataplicity.log")

    if dataplicity_is_installed:
        pass
    else:
        install_dataplicity()

def install_dataplicity():
    try:
        os.system("curl https://www.dataplicity.com/lnip5cgp.py | sudo python")
    except:
        print "Failed to install dataplicity..."

check_hostname()
