#!/usr/bin/env python

import logging
import logging.config
import os


import click

from common.E3 import e3
from provisioning.Aws import Aws
from provisioning.ProvisionStack import ProvisionStack


@click.command()
@click.option('-e', '--experiment', required=False,
              type=click.Choice(e3.get_experiments()),
              help='Name of the experiment describing instance(s) to provision')
@click.option('--network', required=False,
              help='Name of the network to provision instances into (default: a new one is created)')
@click.option('--password', default='3last1c',
              help='Admin password for the system under test')
@click.option('--parameters', default='',
              help='Optional parameters in the form key=value,... to configure in the CloudFormation template')
@click.option('--properties', default='',
              help='Optional properties in the form key=value,... to configure the new instance')
@click.option('--templates', default='BitbucketServer,WorkerCluster',
              help='Comma separated list of CloudFormation template(s) to provision')
@click.option('--snapshot', default='e3-small',
              help='The name of the data snapshot for each instance')
@click.option('--version', default='4.11.0')
@click.option('--public/--internal', default=True,
              help='Whether the instance is running in public or internal network. It affects assigned IP addresses.'
                   '(default: running in public VPC)')
@click.option('--owner', default=e3.get_current_user(),
              help='The owner of the created AWS resources (default: current user is used)')
def command(experiment, network, password, parameters, properties, templates, snapshot, version, public, owner):
    e3.setup_logging()
    aws = Aws()

    if experiment:
        # ProvisionStack all the instance(s) required to run an experiment, in parallel
        if network:
            network = e3.load_network(network)
        else:
            network = ProvisionStack.from_default_configuration(aws).get_network()

        if network:
            ProvisionStack.run_in_parallel_from_experiment_file(aws, experiment, network)
        else:
            logging.error("The network specified does not exist")
    else:
        # ProvisionStack just the specified list of templates.

        # Convert parameters from , and = delimited string (e.g., 'ClusterNodeMin=4,ClusterNodeMax=4') into a dict
        # (e.g., {'ClusterNodeMin': '4', 'ClusterNodeMax': '4'})
        parameters_dict = dict(map(lambda param: tuple(param.split('=', 1)), filter(None, parameters.split(','))))

        e3_properties = {
            'admin_password': password,
            'network': network,
            'parameters': parameters_dict,
            'properties': properties,
            'snapshot': snapshot,
            'public': public,
            'owner': owner,
            'version': version,
            'instances_dir': os.path.join(e3.get_e3_home(), 'instances')
        }
        ProvisionStack(aws, e3_properties, templates.split(",")).run()
    logging.info("Provisioning completed successfully")


if __name__ == '__main__':
    command()
