import requests
import sys
import json
import os
import urllib2

CONFIG_PATH = '/home/pi'

def check_if_offline():
    config = load_config_file()
    if config['settings']['state'] == 'online':
        load_log_file(config)

def load_config_file():
    baseurl = "http://127.0.0.1:3000/getConfig"

    try:
        result = urllib2.urlopen(baseurl)
    except urllib2.URLError as e:
        os.system("sudo reboot now")

    config = json.loads(result.read())
    return config

def load_log_file(config):
    log_file = CONFIG_PATH + "/nycts-unit/logs/logs.json"
    try:
        with open(log_file, "rb") as f:
            payload = f.read()
    except Exception, e:
            payload = {}
    upload_log(config, log_file, payload)

def upload_log(config, log_file, payload):
    client_id = config['settings']['client_id']
    url = "https://api.trainsignapi.com/prod-logs/logs/" + client_id + "/upload"
    headers = {
        'content-type': "application/octet-stream",
        'x-api-key': config['settings']['prod_api_key']
        }
    requests.request(
        "POST", url, data=payload, headers=headers, params=querystring)
    wipe_log_file(log_file)

def wipe_log_file(log_file):
    try:
        open(log_file, 'w').close()
    except Exception, e:
        pass

check_if_offline()
quit()
