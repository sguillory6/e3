#!/usr/bin/env python

import logging
import logging.config
import traceback

import click
import sys

from Analyze import run_rrd_analysis
from Deprovision import Deprovision
from Gather import Gather
from Run import Run
from common.E3 import e3
from provisioning.Aws import Aws
from provisioning.ProvisionStack import ProvisionStack

experiments_dir = "%s/experiments" % e3.get_e3_home()
instances_dir = "%s/instances" % e3.get_e3_home()


class Orchestrate:
    def __init__(self, experiment_name, network, retain):
        self.log = logging.getLogger('orchestrate')
        self.aws = Aws()
        if network:
            self.network = e3.load_network(network)
        else:
            self.network = ProvisionStack.from_default_configuration(self.aws).get_network()
        self.experiment = e3.load_experiment(experiment_name)
        self.experiment_name = experiment_name
        self.retain = retain

    def run(self):
        run_name = None
        try:
            # ProvisionStack all the instances and workers in parallel
            run = ProvisionStack.run_in_parallel_from_experiment_file(self.aws, self.experiment_name, self.network)
            run_name = run['run_name']

            # Run the experiment
            Run(run_name).run()

            # Gather experiment data off the instances
            Gather(run_name).gather()

            try:
                # TODO add the gnuplot based analysis
                run_rrd_analysis(run_name)
            except Exception as e:
                traceback.print_exc()
                self.log.error(e)

            if not self.retain:
                self.log.info("Deleting provisioned CloudFormation stacks")
                Deprovision(run_name).deprovision()

        except Exception as e:
            traceback.print_exc(file=sys.stderr)
            self.log.error(e)
            Deprovision(run_name).deprovision()



@click.command()
@click.option('-e', '--experiment', required=True, help='The experiment you want to run',
              type=click.Choice(e3.get_experiments()))
@click.option('-n', '--network', required=False, help='The network your experiment will be run against',
              type=click.Choice(e3.get_networks()))
@click.option('-r', '--retain', required=False, help='Retain any provisioned aws resources', default=True)
def command(experiment, network, retain):
    logging.config.fileConfig(e3.get_logging_conf())
    Orchestrate(experiment, network, retain).run()


if __name__ == '__main__':
    command()
