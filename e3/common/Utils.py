import logging
import os
import subprocess
import sys
import threading
import time
import traceback

import datetime
import requests
import spur
from requests.exceptions import ConnectTimeout, ConnectionError

FNULL = open(os.devnull, 'w')
__LAUNCH_EXTERNAL_VIEWER__ = [True]


def quote_if_necessary(s):
    if ' ' in s:
        return '"' + s + '"'
    else:
        return s


def rsync(ec2_ip, key_file, ec2_file, local_file, upload=True):
    if ec2_ip == 'localhost':
        rsync_local(local_file, ec2_file)
    else:
        rsync_remote(ec2_ip, key_file, ec2_file, local_file, upload=upload)


def rsync_local(source, destination):
    stdout = LogWrapper("localhost", LogWrapper.stdout)
    stderr = LogWrapper("localhost", LogWrapper.stderr)
    spur.LocalShell().run(["rsync", "-vazrq", source, destination], stderr=stderr, stdout=stdout, allow_error=True)


def rsync_remote(ec2_ip, key_file, ec2_file, local_file, upload=False):
    stdout = LogWrapper("localhost", LogWrapper.stdout)
    stderr = LogWrapper("localhost", LogWrapper.stderr)

    remote_file = "%s:%s" % (ec2_ip, ec2_file)

    source = local_file if upload else remote_file
    destination = remote_file if upload else local_file

    command = ["rsync", "-azrq", "-e",
               "ssh -i %s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" % key_file, source, destination]
    spur.LocalShell().run(command, stderr=stderr, stdout=stdout, allow_error=True)


def now():
    return datetime.datetime.now().replace(microsecond=0)


def disable_external_tool():
    global __LAUNCH_EXTERNAL_VIEWER__
    __LAUNCH_EXTERNAL_VIEWER__[0] = False


def open_with_external_tool(resources_to_open):
    """
    Opens the specified resources with an external tool, based on the OS
    :param resources_to_open: The resources to open
    :type resources_to_open: list(str)
    :return: Nothing
    :rtype: None
    """
    # Open the resulting images using the system "open" or "see" command
    global __LAUNCH_EXTERNAL_VIEWER__
    if __LAUNCH_EXTERNAL_VIEWER__[0]:
        if not try_open_with('open', resources_to_open):
            # open failed, try see
            if not try_open_with('see', resources_to_open):
                # On linux the gnome-open and xdg-open takes only one file at a time
                for resource_to_open in resources_to_open:
                    # see failed, try gnome-open
                    if not try_open_with('gnome-open', resource_to_open):
                        # gnome-open failed, try xdg-open
                        if not try_open_with('xdg-open', resource_to_open):
                            # all failed, print the names of the images
                            print("Output images: %s" % resource_to_open)


def poll_url(url, max_poll_time_seconds, success_callback):
    log = logging.getLogger("util")
    start_time = now()
    log.info("Polling url: %s" % url)

    while True:
        try:
            response = requests.get(url, timeout=60)
            success = success_callback(response)
            log.debug(".")
            if success:
                log.info("Achieved desired response from url %s in %s seconds", url, now() - start_time)
                return True
            time.sleep(15)
        except (ConnectTimeout, ConnectionError):
            pass
        finally:
            if (now() - start_time).seconds > max_poll_time_seconds:
                log.warn("Timed out polling for response from %s", url)
                return False


def try_open_with(utility, resources_to_open):
    """
    Try and open the specified resource with the specified utility
    :param utility: The utility to use (i.e. open, see, gnome-open)
    :param resources_to_open: A list of resources to open
    :type resources_to_open: list(str)
    :return: True if opened, else False
    :rtype: bool
    """
    try:
        if isinstance(resources_to_open, list):
            cmd = [utility] + resources_to_open
        elif isinstance(resources_to_open, str):
            cmd = [utility] + [resources_to_open]
        else:
            return False
        logging.debug("Running command: %s" % cmd)
        subprocess.call(cmd)
        return True
    except StandardError:  # The base exception for most exception types
        return False


class LogWrapper:
    stdout = "STDOUT"
    stderr = "STDERR"
    """
    Note this class is _not_ threadsafe it wraps a logger with a "write" method so that the output of remote commands
    can be streamed to the logger
    """

    def __init__(self, hostname, name):
        self.parent_thread = threading.currentThread().getName()
        self._log = logging.getLogger("command")
        self.hostname = hostname
        self.buffer = []
        self.extra_log_arguments = {'parent_thread': str(self.parent_thread),
                                    'hostname': str(self.hostname),
                                    'out_name': name}

    def write(self, message):
        try:
            if message == '\n':
                message = "".join(self.buffer)
                if isinstance(message, unicode):
                    self._log.debug(unicode.decode(message, errors="ignore"), extra=self.extra_log_arguments)
                else:
                    self._log.debug(message, extra=self.extra_log_arguments)
                self.buffer = []
            else:
                self.buffer.append(message)
        except Exception as ex:
            traceback.print_exc(file=sys.stderr)
            print "Exception logging remote command %s" % ex
