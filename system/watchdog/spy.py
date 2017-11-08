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
    time.sleep(10)
    while (os.system("ping -c 1 google.com") == 0):
        try:
            print "Installing dataplicity..."
            os.system("sudo python /home/pi/nycts-unit/system/install/dataplicity.py")
            upload_unit_model()
            print "something"
            os.system("sudo reboot now")
        except:
            print "Failed to install dataplicity..."
            install_dataplicity()
        time.sleep(1)
    return False

def upload_unit_model():
    config = load_config_file()
    sign_id = config['settings']['sign_id']
    client_id = config['settings']['client_id']
    versions = load_version_file()

    url = "https://api.trainsignapi.com/prod-version-handshake/handshake"
    headers = {
        'content-type': "application/octet-stream",
        'x-api-key': config['settings']['prod_api_key']
        }
    payload = {
        "client_id": client_id,
		"sign_id": sign_id,
		"model": versions['model'],
		"firmware": versions['firmware']
        }
    requests.request(
        "POST", url, data=payload, headers=headers)

def load_version_file():
    VERSION_PATH = '/home/pi/nycts-unit/api/version.json'

    with open(VERSION_PATH) as json_file:
        return json.load(json_file)

check_hostname()
