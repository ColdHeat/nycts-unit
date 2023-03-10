import subprocess
import psutil
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

def check_system_state():
    if base().config['settings']['run_speed_test'] == True:
        check_internet_speed()
    run_system_diagnostics()

def run_system_diagnostics():
    logs.logger.info(
        'System Diagnostic', extra={
            'status': 1,
            'cpu_usage': psutil.cpu_percent(interval=1),
            'virtual_memory': psutil.virtual_memory()[2],
            'swap_memory': psutil.swap_memory()[3],
            'disk_usage': psutil.disk_usage('/')[3],
            'temp': convert_temperature() })

def check_internet_speed():
    speed_data = subprocess.check_output(['speedtest-cli', '--json'])

    logs.logger.info(
        'Speed Test', extra={
            'status': 0, 'job':'speed_test'})

def convert_temperature():
    temp = subprocess.check_output(
        ['cat', '/sys/class/thermal/thermal_zone0/temp'])

    return  str(((int(temp))/1000) * 9/5 + 32) + ' F'

check_system_state()
