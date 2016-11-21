#!/usr/bin/env python

import logging
import logging.config

import click

from common.E3 import e3
from provisioning.Aws import Aws


class Deprovision:
    def __init__(self, run_name):
        self._aws = Aws()
        self._log = logging.getLogger('deprovision')
        self._run_name = run_name
        self._run_json = e3.load_run(run_name)

    def deprovision(self, retain_network=False):
        for thread in self._run_json['threads']:
            worker = thread['worker']
            if 'stack' in worker:
                worker_stack_name = worker['stack']['Name']
                self._log.info("Deleting stack %s" % worker_stack_name)
                self._aws.cloud_formation.Stack(worker_stack_name).delete()
                # Delete the network
                if not retain_network:
                    if 'RunConfig' in worker['stack']:
                        network_stack_name = worker['stack']['RunConfig']['network']
                        self._log.info("Deleting stack %s" % network_stack_name)
                        self._aws.cloud_formation.Stack(network_stack_name).delete()
            instance = thread['instance']
            if 'stack' in instance:
                instance_stack_name = instance['stack']['Name']
                self._log.info("Deleting stack %s" % instance_stack_name)
                self._aws.cloud_formation.Stack(instance_stack_name).delete()
                # Delete the network
                if not retain_network:
                    if 'RunConfig' in instance['stack']:
                        network_stack_name = instance['stack']['RunConfig']['network']
                        self._log.info("Deleting stack %s" % network_stack_name)
                        self._aws.cloud_formation.Stack(network_stack_name).delete()

        try:
            e3.archive_run(self._run_name)
        except OSError:
            self._log.error("Unable to archive run '%s' to archive folder, please delete or move it manually",
                            self._run_name)


@click.command()
@click.option('-r', '--run', required=True, help='The experiment run you want to tear down',
              type=click.Choice(e3.get_runs()))
@click.option('-n', '--network', required=False, is_flag=True, default=False,
              help='When specified the network associated with the stack will be retained')
def command(run, network):
    logging.config.fileConfig(e3.get_logging_conf())
    Deprovision(run).deprovision(network)

if __name__ == '__main__':
    command()
