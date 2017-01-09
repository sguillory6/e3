#!/usr/bin/env python

import os
import logging
import logging.config
import click

from common.E3 import e3
from provisioning.Aws import Aws


class Deprovision:
    def __init__(self, run_name, remove_all_instances=False):
        self._aws = Aws()
        self._log = logging.getLogger('deprovision')
        self._run_name = run_name
        self._remove_all_instances = remove_all_instances
        self._run_json = None
        if run_name:
            self._run_json = e3.load_run(run_name)

    def deprovision(self, retain_network=False):
        if self._run_json:
            for thread in self._run_json['threads']:
                worker = thread['worker']
                if 'stack' in worker:
                    worker_stack_name = worker['stack']['Name']
                    self._deprovision_instance(worker_stack_name)
                    # Delete the network
                    if not retain_network:
                        if 'RunConfig' in worker['stack']:
                            network_stack_name = worker['stack']['RunConfig']['network']
                            self._deprovision_instance(network_stack_name)
                instance = thread['instance']
                if 'stack' in instance:
                    instance_stack_name = instance['stack']['Name']
                    self._deprovision_instance(instance_stack_name)
                    # Delete the network
                    if not retain_network:
                        if 'RunConfig' in instance['stack']:
                            network_stack_name = instance['stack']['RunConfig']['network']
                            self._deprovision_instance(network_stack_name)

            try:
                e3.archive_run(self._run_name)
            except OSError:
                self._log.error("Unable to archive run '%s' to archive folder, please delete or move it manually",
                                self._run_name)
        else:
            if self._remove_all_instances:
                logging.info("Deleting all running stacks")
                self._deprovision_all_instances()
            else:
                running_stack_json = e3.load_instance(self._run_name)
                if running_stack_json:
                    logging.info("Deleting stack %s" % running_stack_json["StackId"])
                    self._deprovision_instance(running_stack_json["StackId"])
                else:
                    logging.info("Please provide experiment name or instance name")

    def _deprovision_all_instances(self):
        # Loop all running instances in home folder to delete
        exp = os.path.join(e3.get_e3_home(), "instances")
        for running_stack_file in e3.get_stacks():
            running_stack_name = running_stack_file[len('stack-'):-len('.json')]
            try:
                self._deprovision_instance(running_stack_name)
                os.remove(running_stack_name)
            except:
                logging.error("Could not delete stack %s" % running_stack_name)

    def _deprovision_instance(self, instance_stack_name):
        self._log.info("Deleting stack %s" % instance_stack_name)
        self._aws.cloud_formation.Stack(instance_stack_name).delete()


@click.command()
@click.option('-r', '--run', required=False, help='The experiment/stack run you want to tear down',
              type=click.Choice(e3.get_runs_name() + e3.get_stacks()))
@click.option('-all', '--all_instances', required=False, is_flag=True, default=False,
              help='Tear down all running instances in home/instances folder')
@click.option('-n', '--network', required=False, is_flag=True, default=False,
              help='When specified the network associated with the stack will be retained')
def command(run, all_instances, network):
    e3.setup_logging()
    Deprovision("stack-confluence-data-center-dluong-9be907", all_instances).deprovision(network)

if __name__ == '__main__':
    command()
