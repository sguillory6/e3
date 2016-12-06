#!/usr/bin/env python

import os

import click
import logging
import logging.config

import shutil

from common import Utils
from common.Config import run_config
from common.E3 import e3


class Gather:
    def __init__(self, run_name):
        self._run = e3.load_run(run_name)
        self._run_name = run_name

    def gather(self):
        # Gather run data off the instances
        thread_index = 1
        for thread in self._run['threads']:
            thread_name = 'thread-%03d' % thread_index
            self.rsync_worker(thread['worker']['stack']['Name'], thread_name, self._run_name)
            self.rsync_instance(thread['instance']['stack']['Name'], thread_name, self._run_name)
            thread_index += 1

    def rsync_worker(self, worker_name, thread_name, run_name):
        worker = e3.load_instance(worker_name)
        key_file = '%s/instances/%s.pem' % (e3.get_e3_home(), worker_name)
        number = 1
        for node in worker['ClusterNodes']:
            directory = '%s/runs/%s/%s/worker-node-%03d' % (e3.get_e3_home(), run_name, thread_name, number)
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.makedirs(directory)
            collectd_csv_directory = '%s/runs/%s/%s/worker-node-%03d/collectd-csv' % \
                                     (e3.get_e3_home(), run_name, thread_name, number)
            if not os.path.exists(collectd_csv_directory):
                os.makedirs(collectd_csv_directory)
            collectd_rrd_directory = '%s/runs/%s/%s/worker-node-%03d/collectd-rrd' % \
                                     (e3.get_e3_home(), run_name, thread_name, number)
            if not os.path.exists(collectd_rrd_directory):
                os.makedirs(collectd_rrd_directory)
            Utils.rsync(node, key_file, '%s/runs/%s/' % (run_config(node)['data_dir'], run_name),
                        directory, upload=False)
            Utils.rsync(node, key_file, '/var/lib/collectd/csv/', collectd_csv_directory, upload=False)
            Utils.rsync(node, key_file, '/var/lib/collectd/rrd/', collectd_rrd_directory, upload=False)
            number += 1

    def rsync_instance(self, instance_name, thread_name, run_name):
        instance = e3.load_instance(instance_name)
        key_file = '%s/instances/%s.pem' % (e3.get_e3_home(), instance_name)
        number = 1
        for node in instance['ClusterNodes']:
            directory = '%s/runs/%s/%s/cluster-node-%03d' % (e3.get_e3_home(), run_name, thread_name, number)
            collectd_cvs_directory = '%s/runs/%s/%s/cluster-node-%03d/collectd-csv' % \
                                     (e3.get_e3_home(), run_name, thread_name, number)
            if not os.path.exists(collectd_cvs_directory):
                os.makedirs(collectd_cvs_directory)
            collectd_rrd_directory = '%s/runs/%s/%s/cluster-node-%03d/collectd-rrd' % \
                                     (e3.get_e3_home(), run_name, thread_name, number)
            if not os.path.exists(collectd_rrd_directory):
                os.makedirs(collectd_rrd_directory)
            Utils.rsync(node, key_file, '/var/atlassian/application-data/bitbucket/log', directory, upload=False)
            Utils.rsync(node, key_file, '/var/lib/collectd/csv/', collectd_cvs_directory, upload=False)
            Utils.rsync(node, key_file, '/var/lib/collectd/rrd/', collectd_rrd_directory, upload=False)
            number += 1

        file_server = instance['FileServerConnectionString']
        if file_server:
            collectd_cvs_directory = '%s/runs/%s/%s/file-server-001/collectd-csv' % \
                                     (e3.get_e3_home(), run_name, thread_name)
            if not os.path.exists(collectd_cvs_directory):
                os.makedirs(collectd_cvs_directory)
            collectd_rrd_directory = '%s/runs/%s/%s/file-server-001/collectd-rrd' % \
                                     (e3.get_e3_home(), run_name, thread_name)
            if not os.path.exists(collectd_rrd_directory):
                os.makedirs(collectd_rrd_directory)
            Utils.rsync(file_server, key_file, '/var/lib/collectd/csv/', collectd_cvs_directory, upload=False)
            Utils.rsync(file_server, key_file, '/var/lib/collectd/rrd/', collectd_rrd_directory, upload=False)


@click.command()
@click.option('-r', '--run', required=True, help='The experiment run you want to gather',
              type=click.Choice(e3.get_runs()), default=e3.get_single_run())
def command(run):
    e3.setup_logging()
    Gather(run).gather()

if __name__ == '__main__':
    command()
