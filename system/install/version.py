import requests
import sys
import json
import os

def upload_unit_model():
    config = load_config_file()
    sign_id = config['settings']['sign_id']
    client_id = config['settings']['client_id']
    versions = load_version_file()

    url = "https://api.trainsignapi.com/prod-version-handshake/handshake"
    headers = {
        'content-type': "application/json",
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

upload_unit_model()
