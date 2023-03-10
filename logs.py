import logging
import json
import json_log_formatter
import requests

formatter = json_log_formatter.JSONFormatter()
json_handler = logging.FileHandler(filename='logs/logs.json')
json_handler.setFormatter(formatter)
logger = logging.getLogger('log')
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)
