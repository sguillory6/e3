import datetime
import logging
import os
import subprocess
import time

import requests
from requests.exceptions import ConnectTimeout, ConnectionError

FNULL = open(os.devnull, 'w')


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
    subprocess.call(["rsync", "-vazrq", source, destination], stderr=FNULL)


def rsync_remote(ec2_ip, key_file, ec2_file, local_file, upload=False):
    remote_file = "%s:%s" % (ec2_ip, ec2_file)

    # print 'ec2_file=%s' % ec2_file
    # print 'local_file=%s' % local_file

    source = local_file if upload else remote_file
    destination = remote_file if upload else local_file

    command = ["rsync", "-azrq", "-e",
                    "ssh -i %s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" % key_file, source,
                    destination]
    print " ".join(map(quote_if_necessary, command))

    # TODO this method does not fail if rsync fails. Update this to fail and report an error
    subprocess.call(command, stderr=FNULL)


def now():
    return datetime.datetime.now().replace(microsecond=0)


def open_with_external_tool(resources_to_open):
    """
    Opens the specified resources with an external tool, based on the OS
    :param resources_to_open: The resources to open
    :type resources_to_open: list(str)
    :return: Nothing
    :rtype: None
    """
    # Open the resulting images using the system "open" or "see" command
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


def poll_url(url, max_poll_time, success_callback):
    log = logging.getLogger("util")
    start_time = now()
    log.info("Polling url: %s" % url)

    while True:
        try:
            response = requests.get(url, timeout=60)
            success = success_callback(response)
            log.debug(".")

            if success:
                log.info("Achieved desired response from url %s in %s seconds", url,
                         datetime.datetime.now().replace(microsecond=0) - start_time)
                return True
            time.sleep(15)
        except (ConnectTimeout, ConnectionError):
            pass
        finally:
            if (now() - start_time).seconds > max_poll_time:
                log.warn("Timed out polling for response from %s", url)
                return False


def run_script_over_ssh(user_host, key_file, file_name):
    subprocess.call(["ssh", "-n", "-f", "-i%s" % key_file, "-t", "-t", "-o UserKnownHostsFile=/dev/null",
                     "-o StrictHostKeyChecking=no", user_host,
                     "bash -c 'nohup sh %s > output.out 2> output.err < /dev/null'" % file_name])


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
