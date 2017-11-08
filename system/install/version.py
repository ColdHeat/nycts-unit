import requests
import sys
import json
import os
import urllib2
import sys
sys.path.insert(0, '/home/pi/nycts-unit')
import logs

def load_config_file():
    baseurl = "http://127.0.0.1:3000/getConfig"
    try:
        result = urllib2.urlopen(baseurl)
    except urllib2.URLError as e:
        sys.exit()
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
    sign_id = config['settings']['sign_id']
    url = "https://api.trainsignapi.com/prod-logs/logs/" + sign_id + "/upload"
    headers = {
        'content-type': "application/octet-stream",
        'x-api-key': config['settings']['prod_api_key']
        }
    requests.request(
        "POST", url, data=payload, headers=headers)
    wipe_log_file(log_file)

def wipe_log_file(log_file):
    try:
        open(log_file, 'w').close()
    except Exception, e:
        sys.exit()

check_if_offline()
