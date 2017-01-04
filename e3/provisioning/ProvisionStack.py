import json
import logging
import os
import requests
from datetime import datetime
from threading import Lock, Thread

import boto3

from common.E3 import e3
from provisioning.BitbucketDataCenter import BitbucketDataCenter
from provisioning.BitbucketDataCenterLDAP import BitbucketDataCenterLDAP
from provisioning.BitbucketServer import BitbucketServer
from provisioning.BitbucketServerGenerateDataset import BitbucketServerGenerateDataSet
from provisioning.PublicNetwork import PublicNetwork
from provisioning.WorkerCluster import WorkerCluster


class ProvisionStack:
    """Provisions AWS stacks for use with E3"""
    def __init__(self, aws, e3_properties, template_names):
        boto3.set_stream_logger('boto3', logging.WARN)

        self._available_templates = {
            "BitbucketDataCenter": BitbucketDataCenter(aws, e3_properties),
            "BitbucketDataCenterLDAP": BitbucketDataCenterLDAP(aws, e3_properties),
            "BitbucketServer": BitbucketServer(aws, e3_properties),
            "BitbucketServerGenerateDataSet": BitbucketServerGenerateDataSet(aws, e3_properties),
            "WorkerCluster": WorkerCluster(aws, e3_properties),
            "PublicNetwork": PublicNetwork(aws, e3_properties)
        }
        self._aws = aws
        self._e3_properties = e3_properties

        existing_nw = self._e3_properties.get('network', None)
        if existing_nw and len(existing_nw) > 0:
            self._network = e3.load_network(existing_nw)
        else:
            self._network = self.provision('PublicNetwork')

        self._e3_properties['vpc'] = self._network['VPC']
        self._e3_properties['subnet1'] = self._network['Subnet1']
        self._e3_properties['subnet2'] = self._network['Subnet2']

        self._log = logging.getLogger('provision')
        self._template_names = template_names

    def get_network(self):
        return self._network

    @classmethod
    def from_default_configuration(cls, aws):
        return cls(aws, {
            'admin_password': 'admin',
            'properties': '',
            'public': 'true',
            'parameters': '',
            'owner': e3.get_current_user(),
            'snapshot': ''
        }, "")

    @classmethod
    def run_in_parallel_from_experiment_file(cls, aws, experiment_name, network):
        run_name = "%s-%s" % (experiment_name, datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        run_dir = os.path.join(e3.get_run_dir(), run_name)
        logging.getLogger('provision').info("Creating %s for all experiment run data", os.path.abspath(run_dir))
        os.makedirs(run_dir)

        experiment = e3.load_experiment(experiment_name)
        if experiment is None:
            raise ValueError("Unable to load experiment JSON for experiment with name: '%s'" % experiment_name)

        k = 0
        threads = []
        instances_to_provision = \
            map(lambda x: x['instance'], experiment['threads']) + \
            map(lambda x: x['worker'], experiment['threads'])

        experiment['run_name'] = run_name
        flush_lock = Lock()

        for instance in instances_to_provision:
            def flush():
                with flush_lock:
                    # Save a copy of the full experiment configuration (with all stacks populated) in the run directory.
                    with open(os.path.join(run_dir, '%s.json' % run_name), 'w') as jsonFile:
                        json.dump(experiment, jsonFile)

            provisioning_thread = ProvisionWorker(aws, instance, network, k, flush)
            threads.append(provisioning_thread)
            provisioning_thread.start()
            k += 1
        for thread in threads:
            thread.join()

        return experiment

    def provision(self, template_name):

        template = self._available_templates[template_name]
        stack_name = template.get_stack_name()

        template.before_provision()

        stack_config = template.get_stack_config()
        cf_template = stack_config["Template"]
        file_name = "%s.template" % cf_template
        local_template_dir = e3.get_template_dir()
        template_kwargs = {}
        template_body = None

        template_url = e3.get_template_url(template_name)
        if template_url:
            print template_url
            res = requests.get(template_url)
            if res.status_code == 200:
                template_body = res.text

        if local_template_dir:
            print "Checking local directory for template"
            file_path = os.path.join(local_template_dir, file_name)
            if os.path.isfile(file_path):
                print "Using local template '%s'" % file_name
                with open(file_path, "r") as template_file:
                    template_body = template_file.read()

        if template_body:
            template_kwargs['TemplateBody'] = template_body
        else:
            template_kwargs['TemplateURL'] = "https://s3.amazonaws.com/%s/%s" % (e3.get_s3_bucket(), file_name)

        print "Creating stack from CloudFormation template %s" % cf_template
        self._aws.cloud_formation.create_stack(
            Capabilities=['CAPABILITY_IAM'],
            Parameters=template.generate_parameters(),
            StackName=stack_name,
            Tags=template.generate_tags(),
            DisableRollback=True,
            **template_kwargs)

        template.wait_stack_status()

        stack_name = stack_config["StackName"]
        stack = self._aws.cloud_formation.Stack(stack_name)
        for i in stack.outputs:
            stack_config["Output"][i['OutputKey']] = i['OutputValue']
        stack_config["Output"]['StackId'] = stack.stack_id
        stack_config["Output"]['snapshot'] = self._e3_properties['snapshot']
        stack_config["Output"]['RunConfig'] = self._e3_properties
        stack_config["Output"]["Name"] = stack_name

        template.after_provision()

        # Save a copy of the instance result in an instances/*.json file.
        output_file_path = os.path.join(e3.get_e3_home(), 'instances', stack_name)
        with open(output_file_path + '.json', 'w') as jsonFile:
            json.dump(stack_config["Output"], jsonFile)

        return stack_config["Output"]

    def run(self):
        for template_name in self._template_names:
            print "Provisioning template %s" % template_name
            self.provision(template_name)


class ProvisionWorker(Thread):
    def __init__(self, aws, instance, network, instance_count, on_complete=None):
        Thread.__init__(self, name='ProvisionWorker:%d' % instance_count)
        self._aws = aws
        self._instance = instance
        self._log = logging.getLogger('provision')
        self._network = network
        self._on_complete = on_complete

    def run(self):
        e3_properties = {
            'admin_password': '3last1c',
            'instances_dir': os.path.join(e3.get_e3_home(), 'instances'),
            'network': self._network['Name'],
            'public': 'true',
            'owner': e3.get_current_user(),
            'properties': '',
            'snapshot': ''
        }

        e3_properties.update(self._instance)
        if 'properties' in self._instance:
            e3_properties['properties'] = ",".join(self._instance['properties'])

        provision_stack = ProvisionStack(self._aws, e3_properties, '')
        self._instance['stack'] = provision_stack.provision(self._instance['template'])

        if self._on_complete:
            self._on_complete()
