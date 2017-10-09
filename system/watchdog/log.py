import requests
import sys
import json
import os
from base import base

COFNIG_PATH = '/home/pi'

def check_if_offline():
    config = base().config

    if config['settings']['state'] == 'offline':
        pass
    else:
        load_log_file(config)

def load_log_file(config):
    file_path = COFNIG_PATH + "/nycts-unit/logs/logs.json"

    try:
        with open(file_path, "rb") as f:
            payload = f.read()
    except:
        payload = {}

    upload_log(config, log_file)

def upload_log(config, log_file, payload):
    client_id = config['settings']['client_id']

    url = "https://api.trainsignapi.com/prod-logs/logs/" + client_id + "/upload"

    querystring = {
        client_id: client_id
        }

    headers = {
        'content-type': "application/octet-stream",
        'x-api-key': config['settings']['prod_api_key']
        }

    requests.request(
        "POST", url, data=payload, headers=headers, params=querystring)

def wipe_log_file(file_path):
    try:
        open(file_path, 'w').close()
    except:
        pass
