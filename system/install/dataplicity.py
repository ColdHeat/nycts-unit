#!/usr/bin/env python2.7
"""
Installer for the Dataplicity agent.

This script prepares your Raspberry Pi or other Linux device for use
with the Dataplicity agent, an open source application that powers
remote terminals and other features on https://www.dataplicity.com

See the following repository on GitHub for the source to the agent:

https://github.com/wildfoundry/dataplicity-agent

"""

from __future__ import division, print_function, unicode_literals

import datetime
import inspect
import json
import locale
import os
import platform
import pwd
import subprocess
import sys
import time
import traceback
import urllib
import urllib2
from functools import partial


# Personalized settings for the installer
SETTINGS = """
{
    "agent_download_url": "https://github.com/wildfoundry/dataplicity-agent/releases/download/v0.4.27/dataplicity",
    "report_url": "https://www.dataplicity.com/installer_event/",
    "api_url": "https://api.dataplicity.com/",
    "m2m_url": "wss://m2m.dataplicity.com/m2m/",
    "time": 1509729820.348083,
    "token": "lnip5cgp",
    "register_url": "https://www.dataplicity.com/install/",
    "agent_version": "v0.4.27",
    "dry_run": false,
    "interactive": true,
    "device_url": "https://www.dataplicity.com/devices/"
}
"""
settings = json.loads(SETTINGS)


AGENT_BASE_PATH = '/opt/dataplicity/agent'
AUTH_PATH = '/opt/dataplicity/tuxtunnel/auth'
CPU_INFO_PATH = "/proc/cpuinfo"
DOWNLOAD_CHUNK_SIZE = 16384
LOG_PATH = "/var/log/dpinstall.log"
MAX_STEPS = 4
SERIAL_PATH = '/opt/dataplicity/tuxtunnel/serial'
SUDOER_LINE = 'dataplicity ALL=(ALL) NOPASSWD: /sbin/reboot'
SUDOERS_PATH = '/etc/sudoers'
SUPERVISOR_CONF_DIR_PATH = '/etc/supervisor/conf.d/'
SUPERVISOR_CONF_PATH = '/etc/supervisor/conf.d/tuxtunnel.conf'


# A string template for the supervisor conf
SUPERVISOR_CONF_TEMPLATE = """
# Installed by Dataplicity Agent installer
[program:tuxtunnel]
environment={ENV}
command={AGENT_PATH} --server-url {API_URL} run
autorestart=true
redirect_stderr=true
user=dataplicity
stdout_logfile=/var/log/dataplicity.log
stderr_logfile=/var/log/dataplicity.log
"""

# Fields from /proc/cpuinfo we want in the report
CPU_INFO_FIELDS = {
    "cpu architecture",
    "cpu implementor",
    "cpu part",
    "cpu revision",
    "cpu variant",
    "hardware"
    "model name",
    "revision"
}

RETURN_SUCCESS = 0
RETURN_USER_ABORT = -1
RETURN_FAIL = -2
RETURN_CRASH = -3


CLOCK_MESSAGE = """\

+----------------------------------------------------------------------+
| The installer has detected your system clock may be wrong!           |
| This may prevent secure downloads from working on your system.       |
| If the install fails, please check your system clock, and try again. |
+----------------------------------------------------------------------+
"""

open_write_binary = lambda path: open(path, 'wb')
open_append_binary = lambda path: open(path, 'ab')
open_append_text = lambda path: open(path, 'at')
open_read_text = lambda path: open(path, 'rt')
open_read_binary = lambda path: open(path, 'rb')
subprocess_check_output = subprocess.check_output
symlink = os.link
rename = os.rename
chmod = os.chmod

# Store the log in memory as well as write to file
install_log = []

# Current step in the installation process, updated by `show_step`
current_step = 0

start_time = time.time()  # time installer started
last_log_time = start_time  # time since last log_time

# Get the start time of the installer, in ISO 8601 format
# This is sent to keen so we can detect incorrect clocks
start_time_iso_8601 = datetime.datetime.utcnow().isoformat()


class AbortInstall(Exception):
    """Installation can not continue."""


def create_log_file():
    """Create (and wipe) log file."""
    try:
        with open_write_binary(LOG_PATH):
            pass
    except IOError:
        # Probably means no permission
        pass


def log(text, *args, **kwargs):
    """Log technical details to LOG_PATH."""
    caller = inspect.stack()[1][3]  # Get the caller function name
    log_text = text.format(*args, **kwargs)
    lines = (log_text + '\n').splitlines()
    install_log.extend(lines)

    write_lines = '\n'.join(
        "{}: {}".format(caller.ljust(16), line)
        for line in lines
    ) + '\n'

    try:
        with open_append_binary(LOG_PATH) as log_file:
            log_file.write(
                write_lines.encode('utf-8', errors='replace')
            )
    except IOError:
        # Probably a permissions error
        pass


def log_time():
    """Log seconds since last call to `log_time`."""
    global last_log_time
    t = time.time()
    log('{:.1f}s elapsed', t - last_log_time)
    last_log_time = t


def user(text, *args, **kwargs):
    """Writes progress information for the user."""
    log_text = text.format(*args, **kwargs)
    print(log_text)
    log(log_text)


def log_exception(msg, *args, **kwargs):
    """Log a traceback."""
    tb = traceback.format_exc()
    log(msg, *args, **kwargs)
    log(tb)


def make_dir(path, mode=0o777, makedirs=None):
    """Make a directory if it does not exist (and intermediate dirs)."""
    try:
        (makedirs or os.makedirs)(path, mode)
    except OSError:
        log('{} (exists)', path)
    else:
        log('{} (created)', path)


def main():
    """Main entry point."""

    def show_help():
        user('See file {} for details.', LOG_PATH)
        user(
            'Email support@dataplicity.com for help, '
            'or visit https://docs.dataplicity.com/'
        )

    try:
        log('-' * 70)
        time_str = datetime.datetime.utcnow().ctime()
        log(time_str)
        log('install started')
        log('')

        # Run the install
        run()

        log('install completed')
    except KeyboardInterrupt:
        report('user-abort')
        log('user pressed Ctrl+C')
        user('Installation canceled.')
        show_help()
        return RETURN_USER_ABORT
    except AbortInstall as e:
        report('fail', reason=str(e))
        log('install aborted ({})', e)
        user('')
        user('{}', e)
        show_help()
        return RETURN_FAIL
    except Exception as e:
        report('crash', reason=str(e))
        log_exception('install failed ({})', e)
        user('')
        user('The installer encountered an error.')
        show_help()
        return RETURN_CRASH
    else:
        report('success')
        return RETURN_SUCCESS
    finally:
        log('leaving main')


def run():
    """Top level procedural code to install agent."""

    art = """\
    ___      _              _ _      _ _
   /   \__ _| |_ __ _ _ __ | (_) ___(_) |_ _   _
  / /\ / _` | __/ _` | '_ \| | |/ __| | __| | | |
 / /_// (_| | || (_| | |_) | | | (__| | |_| |_| |
/___,' \__,_|\__\__,_| .__/|_|_|\___|_|\__|\__, | {agent_version}
                     |_|                   |___/
""".format(agent_version=settings['agent_version'])
    user(art)
    user('Welcome to the Dataplicity Agent Installer')

    # Check the system time
    check_clock(start_time)
    log_info()

    if settings['dry_run']:
        user('dry run enabled - no system changes will be made')

    user('')

    # ------------------------------------------------------------------
    show_step(1, 'downloading open source agent')
    agent_dir = get_agent_dir()
    make_dir(agent_dir)
    agent_path = write_agent(agent_dir, 'dataplicity')
    executable_path = get_executable_path()
    link(agent_path, executable_path)
    make_executable(agent_path)
    log_time()

    # ------------------------------------------------------------------
    show_step(2, "registering device")
    device_url = register_device()
    log_time()

    # ------------------------------------------------------------------
    show_step(3, "configuring system")
    create_user()
    update_sudoers()
    if not apt_update():
        log('Package database update failed, continuing with existing package database...')
    if not apt_get('supervisor'):
        log('failed to install supervisor')
        check_supervisor()
    configure()
    log_time()

    # ------------------------------------------------------------------
    show_step(4, "starting agent")
    if not settings['dry_run']:
        run_system('nohup', 'service', 'supervisor', 'restart')
    log_time()
    congratulations(device_url)


def log_info():
    """Log useful system information."""
    distro = " ".join(platform.linux_distribution())
    log('[LINUX]')
    log('distro={}', distro)
    log('')

    system, node, release, version, machine, processor = \
        platform.uname()

    log('[UNAME]')
    log('system={!r}', system)
    log('node={!r}', node)
    log('release={!r}', release)
    log('version={!r}', version)
    log('machine={!r}', machine)
    log('processor={!r}', processor)
    log('')

    log('[SETTINGS]')
    for k, v in settings.items():
        log('{}={!r}', k, v)
    log('')


def show_step(n, msg):
    """Show current step information."""
    global current_step
    current_step = n
    step_msg = "[[ Step {n} of {max} ]] {msg}".format(
        n=n,
        max=MAX_STEPS,
        msg=msg
    )
    log('-' * 70)
    user(step_msg)


def get_agent_dir():
    """Get the absolute directory where the agent will be stored."""
    agent_dir = os.path.abspath(
        os.path.join(
            AGENT_BASE_PATH,
            settings['agent_version']
        )
    )
    return agent_dir


def get_executable_path():
    """Get the absolute path of the dataplicity executable."""
    # This will reference a symlink
    executable_path = os.path.abspath(
        os.path.join(
            AGENT_BASE_PATH,
            'dataplicity'
        )
    )
    return executable_path


def check_clock(current_time):
    """Check the system clock."""
    if abs(settings['time'] - current_time) > 60 * 60 * 24:
        log('system time is out of sync')
        user(CLOCK_MESSAGE)
        return False
    return True


def download(url, path, urlopen=None):
    """Download a file from `url` to `path`."""
    # Can't use requests, since we can't assume anything re Python env
    log('requesting {}', url)
    url_file = None
    try:
        try:
            url_file = (urlopen or urllib2.urlopen)(url)
        except urllib2.HTTPError as http_error:
            response_code = http_error.code
        else:
            response_code = url_file.getcode()

        if response_code != 200:
            user('unable to open URL {}', url)
            log('failed to download {} code={}', url, response_code)
            return False

        file_size = int(url_file.info().getheader('Content-Length'))
        log('content length is {} bytes', file_size)

        bytes_read = 0
        try:
            log('writing {}', path)
            with open_write_binary(path) as write_file:
                read_chunk = partial(url_file.read, DOWNLOAD_CHUNK_SIZE)
                for chunk in iter(read_chunk, b''):
                    bytes_read += len(chunk)
                    write_file.write(chunk)
                    completed_percentage =\
                        100.0 * (bytes_read / file_size)
                    sys.stdout.write(
                        '\r{:.0f}% '.format(completed_percentage)
                    )
                    sys.stdout.flush()
            sys.stdout.write('\r')
            sys.stdout.flush()
        except IOError as e:
            user('unable to save download ({})', e)
            log_exception('download failed')
            return False
        else:
            log('{} bytes read', bytes_read)

    finally:
        if url_file is not None:
            url_file.close()

    return True


def write_agent(agent_dir, agent_filename):
    """Download agent, return absolute path to agent."""
    # Done atomically with an os.rename, so we never leave part
    # of a binary on disk.
    agent_filename_temp = '~' + agent_filename
    path = os.path.join(agent_dir, agent_filename)
    path_temp = os.path.join(agent_dir, agent_filename_temp)
    download_url = settings['agent_download_url']
    if not download(download_url, path_temp):
        raise AbortInstall('unable to download agent')

    rename(path_temp, path)
    log('renamed {}', path)
    return path


def link(agent_path, executable_path):
    """Link current version of agent."""

    if os.path.exists(executable_path):
        log('removing stale link')
        os.remove(executable_path)

    symlink(agent_path, executable_path)
    log("created {}", executable_path)


def make_executable(path):
    """Make agent executable."""
    chmod(path, 0o755)
    log(path)


def run_system(*command):
    """
    Run a system command, log output, and return a boolean indicating
    success.

    """
    # Paranoia re encoding
    encoding = getattr(sys.stdout, 'encoding', None)
    encoding = encoding or locale.getpreferredencoding() or 'utf-8'
    command_line = ' '.join(command).encode(encoding, errors='ignore')
    log('run {!r}', command_line)
    try:
        output = subprocess_check_output(
            command,
            stderr=subprocess.STDOUT
        )
        returncode = 0
    except OSError as e:
        log('error running "{}" ({})', command_line, e)
        return False
    except subprocess.CalledProcessError as e:
        output = e.output
        returncode = e.returncode
    output_unicode = output.decode(encoding, errors='replace')
    log(output_unicode)
    log('{!r} returned={}', command_line, returncode)
    return returncode == 0


def apt_get(package):
    """Install an apt-get package."""
    log('installing package {}', package)
    if settings['dry_run']:
        return
    return run_system('apt-get', '-y', 'install', package)

def apt_update():
    """Update apt"""
    log('Updating apt')
    if settings['dry_run']:
        return
    return run_system('apt-get', '-y' 'update')


def configure(getpwnam=None):
    """Install supervisor conf."""
    getpwnam = getpwnam or pwd.getpwnam
    agent_path = get_executable_path()

    try:
        dataplicity_user = getpwnam('dataplicity')
    except KeyError:
        log("dataplicity user not found, assuming /home/dataplicity")
        dataplicity_home = "/home/dataplicity"
    else:
        dataplicity_home = dataplicity_user.pw_dir

    # Supervisor doesn't create a new shell, so we must explicitly
    # set standard env vars, in addition to our own.
    env = {
        "DATAPLICITY_M2M_URL": settings['m2m_url'],
        "HOME": dataplicity_home,
        "USER": "dataplicity",
    }

    dataplicity_env = ','.join(
        '{}="{}"'.format(k, v)
        for k, v in sorted(env.items())
    )

    format_args = {
        "ENV": dataplicity_env,
        "HOME": dataplicity_home,
        "API_URL": settings['api_url'],
        "AGENT_PATH": agent_path
    }
    conf = SUPERVISOR_CONF_TEMPLATE.format(**format_args)

    log('writing supervisor conf')
    log(conf)
    log('')

    if settings['dry_run']:
        return

    conf_bytes = conf.encode('utf-8')
    with open_write_binary(SUPERVISOR_CONF_PATH) as f:
        f.write(conf_bytes)

    log("enabling supervisor (fix for https://goo.gl/3pfFiJ)")
    run_system("systemctl", "enable", "supervisor")


def register_device(urlopen=None):
    """
    Register device with the server.

    Returns a URL to the device on success.

    """
    serial = None
    if os.path.isfile(SERIAL_PATH):
        with open(SERIAL_PATH, 'rb') as serial_file:
            serial = serial_file.read().strip().decode('utf-8')
        log('serial exists in {} ({})', SERIAL_PATH, serial)

    urlopen = urlopen or urllib2.urlopen

    register_error_msg =\
        'The installer was unable to contact the Dataplicity server'

    device_name = platform.node() or 'New Device'
    cpu_info = get_cpu_info()
    if cpu_info.get('serial'):
        device_name = '{serial}-{device_name}'.format(
            serial=cpu_info.get('serial'),
            device_name=device_name
        )
    log('device name is {}', device_name)
    register_data = {
        "name": device_name,
        "serial": serial,
        "token": settings["token"]
    }
    post_data = urllib.urlencode(register_data)
    register_url = settings['register_url']
    log('posting to {}', register_url)

    try:
        url_file = urlopen(
            register_url,
            post_data
        )
    except urllib2.HTTPError:
        log_exception('unable to register')
        raise AbortInstall(register_error_msg)

    response_code = url_file.getcode()
    log('response code={}', response_code)
    if response_code != 200:
        log('request failed')
        raise AbortInstall(register_error_msg)

    try:
        response_bytes = url_file.read()
    except IOError:
        raise AbortInstall(register_error_msg)

    try:
        response = json.loads(response_bytes)
    except ValueError:
        log('register URL returned bad JSON')
        log('{!r}', response_bytes)
        raise AbortInstall(register_error_msg)

    serial = response['serial']
    auth = response['auth']
    device_url = response['device_url']
    is_new_device = response['is_new_device']

    if is_new_device:
        write_registration(serial, auth)
    else:
        user('')
        user('  +------------------------------------------------------+')
        user('  | The installer used a pre-existing serial number.     |')
        user('  | To register a new device, please delete this device  |')
        user('  | from the device list view.                           |')
        user('  | https://www.dataplicity.com/devices/                 |')
        user('  +------------------------------------------------------+')
        user('')

    return device_url


def write_value(name, path, value):
    """Write a value to a path."""
    make_dir(os.path.dirname(path))
    try:
        with open_write_binary(path) as fh:
            fh.write(value.encode('utf-8'))
    except IOError:
        log_exception('failed to write {}', name)
        raise AbortInstall('unable to write {}'.format(name))


def write_registration(serial, auth):
    """Write serial and auth."""
    write_value('serial', SERIAL_PATH, serial)
    write_value('auth', AUTH_PATH, auth)


def create_user(getpwnam=None, chown=None, isdir=None):
    """Create a dataplicity user and apply permissions."""

    getpwnam = getpwnam or pwd.getpwnam
    chown = chown or os.chown
    isdir = isdir or os.path.isdir

    log('creating user')
    if not settings['dry_run']:
        try:
            dataplicity_user = getpwnam('dataplicity')
        except KeyError:
            log('adding user')
            make_dir('/home', 0o755)
            run_system('useradd', '-m', 'dataplicity')
        else:
            log('user exists')

            dataplicity_user = getpwnam('dataplicity')
            dataplicity_home = dataplicity_user.pw_dir

            # Old installer didn't create home dirs
            if not isdir(dataplicity_home):
                log('creating home dir')  # needed by pex
                make_dir(dataplicity_home)
                chown(
                    dataplicity_home,
                    dataplicity_user.pw_uid,
                    dataplicity_user.pw_gid,
                )


def update_sudoers():
    """Update sudoers to permit reboot."""
    try:
        with open_read_text(SUDOERS_PATH) as sudoers_file:
            lines = sudoers_file.read().splitlines()

        if SUDOER_LINE not in lines:
            log('adding sudoer line')
            with open_append_text(SUDOERS_PATH) as sudoers_file:
                sudoers_file.write("\n{}\n".format(SUDOER_LINE))
    except IOError as e:
        user(
            '  The installer was unable '
            'to update sudoers automatically.'
        )
        user('  The reboot button may not work.')
        log('unable to write to sudoers file ({})', e)


def check_supervisor(isdir=None):
    """Install supervisor."""
    # apt-get failed
    # But we may still be able to continue if an older version
    # was previously installed
    if not (isdir or os.path.isdir)(SUPERVISOR_CONF_DIR_PATH):
        # Definitely not installed
        user('  The installer was unable to install Supervisor on your system.')
        user('  This may be temporary, you could try again.')
        raise AbortInstall(
            'Unable to install Supervisor'
        )


def congratulations(device_url):
    """Tell the user about install."""
    user('')
    user(
        'Dataplicity agent {agent_version} is now installed.',
        agent_version=settings['agent_version']
    )
    user('Your device will be online in a few seconds.')
    user('')
    if device_url is not None:
        user('Visit the following URL to manage your device:')
        user(
            ' * {device_url}',
            device_url=device_url
        )
    user('')
    user('Do you need help? https://docs.dataplicity.com/')
    user('')


def report(status, reason=None):
    """Report install result to server."""
    log('status={!r} reason={!r}', status, reason)
    _report = build_report(status, reason=reason)
    log("{!r}", _report)
    send_report(_report)


def build_report(status, reason=None):
    """Generate report data for `send_report`."""

    log('{} ({})', status, reason)

    # Get total time to this point (in seconds)
    elapsed = int(time.time() - start_time)
    log('{}s elapsed (total)', elapsed)

    data = {
        "cpu": get_cpu_info(),
        "elapsed": elapsed,
        "os": get_os_info(),
        "reason": reason,
        "start_time": start_time_iso_8601,
    }
    data_json = json.dumps(data)
    report = {
        "data": data_json,
        "status": status,
        "step": current_step,
        "token": settings['token']
    }
    return report


def send_report(report, urlopen=None):
    """Send a reported generated by `build_report`"""
    urlopen = urlopen or urllib2.urlopen
    report_post_body = urllib.urlencode(report)

    report_url = settings['report_url']
    log("sending install report to {}", report_url)

    url_file = None
    try:
        url_file = urlopen(report_url, report_post_body)
        log('response code = {}', url_file.getcode())
        url_file.read()
    except Exception:
        # Nothing much to do, can't break the installer
        log_exception('error sending report')
    finally:
        if url_file is not None:
            url_file.close()


def get_os_info():
    """Get OS information for report."""
    distro = " ".join(platform.linux_distribution())
    system, node, release, version, machine, processor = \
        platform.uname()

    os_info = {
        "distro": distro,
        "system": system,
        "release": release,
        "version": version,
        "machine": machine,
        "processor": processor
    }
    return os_info


def get_cpu_info():
    """Get CPU information we need as a dict."""
    cpu_info = {}
    cpu_info_bytes = read_cpu_info()
    cpu_info_items = parse_cpu_info(cpu_info_bytes)
    # Keys may appear once, we are only interested in the first
    for key, value in cpu_info_items:
        if key in CPU_INFO_FIELDS and key not in cpu_info:
            cpu_info[key] = value
            log('{}={}', key, value)
    return cpu_info


def read_cpu_info(open_cpuinfo=None):
    """Read contents of cpuinfo file, or return empty bytes."""
    try:
        with (open_cpuinfo or open_read_binary)(CPU_INFO_PATH) as fh:
            return fh.read()
    except IOError:
        log('unable to read {}', CPU_INFO_PATH)
        return b''


def parse_cpu_info(info_bytes):
    """Parse cpu info fields in to a sequence of (<name>, <value>)."""
    # This isn't a dict, because some combinations may appear more than
    # once.
    fields = []
    for line in info_bytes.splitlines():
        name, colon, value = line.partition(b':')
        if colon:
            name = name.strip().decode('utf-8', errors='replace')
            value = value.strip().decode('utf-8', errors='replace')
            fields.append((name.lower(), value))
    return fields


def entry_point():
    """Main entry point in to the installer."""
    create_log_file()
    return_code = main() or 0
    log('return={}', return_code)
    return return_code

if __name__ == "__main__":
    sys.exit(entry_point())  # pragma: no cover
