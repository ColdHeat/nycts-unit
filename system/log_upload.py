import requests
import sys
import json
import os

config_path = '/home/pi'

with open(config_path + "/nycts-unit/api/config.json") as json_file:
    config_file = json.load(json_file)

client_id = config_file['settings']['client_id']

url = "https://api.trainsignapi.com/dev-logs/logs/" + client_id + "/upload"

querystring = {client_id: client_id}

file_path = config_path + "/nycts-unit/logs/logs.json"

payload = {'log_file': (None, open(file_path,'rb'))}

headers = {
    'content-type': "application/octet-stream",
    'x-api-key': config_file['settings']['dev_api_key']
    }

response = requests.request("POST", url, files=payload, headers=headers, params=querystring)

open(file_path, 'w').close()
