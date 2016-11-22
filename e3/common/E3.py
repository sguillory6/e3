import getpass
import glob
import importlib
import json
import logging
import logging.config
import os
import sys

import yaml


class E3:
    _config = None
    _config_file_name = "e3.yaml"
    _logging_file_name = "logging.conf"

    def __init__(self):
        config_file = E3._discover_config_file()
        if config_file:
            self._config = self._read_configuration(config_file)
        else:
            message = "Unable to find the '%s' file" % self._config_file_name
            raise IOError(message)

    def get_analysis_dir(self, run):
        return os.path.join(self.get_run_dir(run), 'analysis')

    def get_auth_config(self):
        auth_type = self.get_auth_type()
        auth_config_key = 'aws_auth_%s' % auth_type
        return self._config.get('e3', {auth_config_key: {'config': None}}) \
            .get(auth_config_key).get('config')

    def get_auth_type(self):
        return self._config.get('e3', {'aws_auth_type': None}).get('aws_auth_type')

    def get_e3_home(self):
        e3_home = self._config.get('e3', {'home': None}).get('home')
        if e3_home:
            return os.path.abspath(e3_home)

    def get_experiments(self):
        exp = os.path.join(self.get_e3_home(), "experiments")
        return map(lambda experiment_name: experiment_name[:-5],
                   [os.path.basename(config) for config in glob.glob(os.path.join(exp, '*.json'))])

    def get_networks(self):
        exp = os.path.join(self.get_e3_home(), "instances")
        return map(lambda experiment_name: experiment_name[:-5],
                   [os.path.basename(config) for config in glob.glob(os.path.join(exp, 'network*.json'))])

    def get_runs(self):
        runs_found = []
        run_dir = self.get_run_dir()
        if not os.path.exists(run_dir):
            return runs_found
        for pos_run in os.listdir(run_dir):
            pos_run_dir = os.path.join(run_dir, pos_run)
            if os.path.isdir(pos_run_dir):
                pos_run_file = os.path.join(pos_run_dir, "%s.json" % pos_run)
                if os.path.isfile(pos_run_file):
                    runs_found.append(pos_run)
        return runs_found

    def get_run_dir(self, run_name=None):
        if run_name:
            return os.path.join(self.get_e3_home(), 'runs', run_name)
        else:
            return os.path.join(self.get_e3_home(), 'runs')

    def get_run_instance_files(self, run_name):
        run_json = self.load_run(run_name)
        instances_dir = os.path.join(self.get_e3_home(), 'instances')
        metadata = set()
        for thread in run_json.get('threads', []):
            if 'instance' in thread:
                instance_stack = thread.get('instance', {'stack': None}).get('stack')
                if instance_stack:
                    instance_name = instance_stack.get('Name', None)
                    metadata.add("%s.json" % instance_name)
                    metadata.add("%s.pem" % instance_name)
                    instance_network_name = self._get_stack_network(instance_stack)
                    if instance_network_name:
                        metadata.add("%s.json" % instance_network_name)
                        metadata.add("%s.pem" % instance_network_name)

                worker_stack = thread.get('worker', {'stack': None}).get('stack')
                if worker_stack:
                    worker_name = worker_stack.get('Name', None)
                    metadata.add("%s.json" % worker_name)
                    metadata.add("%s.pem" % worker_name)
                    worker_network_name = E3._get_stack_network(worker_stack)
                    if worker_network_name:
                        metadata.add("%s.json" % worker_network_name)
                        metadata.add("%s.pem" % worker_network_name)
        return map(lambda m: os.path.join(instances_dir, m), metadata)

    def get_single_run(self):
        """
        :return: a run if there is only one found, any other returns ""
        :rtype: str
        """
        runs = self.get_runs()
        if len(runs) == 1:
            return runs[0]
        return ""

    def get_s3_bucket(self):
        return self._config.get('e3', {}).get('s3_bucket', None)

    def get_snapshots(self):
        snap = os.path.join(self.get_e3_home(), "snapshots")
        return map(lambda experiment_name: experiment_name[:-5],
                   [os.path.basename(config) for config in glob.glob(os.path.join(snap, '*.json'))])

    def get_stack_ssh_key(self, stack_name):
        return os.path.join(self.get_e3_home(), "instances", stack_name + '.pem')

    def get_configured_es_s3_bucket(self):
        """
        :return: preconfigured s3 bucket if found in config file, other returns None
        :rtype: str or None
        """
        return self._config.get('e3').get('es_s3_bucket')

    def get_template_dir(self):
        return self._config.get('e3', {}).get('template_dir', None)

    def get_workloads(self):
        wl = os.path.join(self.get_e3_home(), "workloads")
        return map(lambda experiment_name: experiment_name[:-5],
                   [os.path.basename(config) for config in glob.glob(os.path.join(wl, '*.json'))])

    def load_authentication(self):
        auth_type = self.get_auth_type()
        auth_config_key = 'aws_auth_%s' % auth_type
        module_name = self._config.get('e3', {auth_config_key: {'class': None}}).get(auth_config_key).get('class')
        if module_name:
            clazz_name = module_name.split(".").pop()
            security_clazz = getattr(importlib.import_module(module_name), clazz_name)
            return security_clazz(self)

    def load_experiment(self, experiment):
        exp = os.path.join(self.get_e3_home(), "experiments", "%s.json" % experiment)
        if os.path.exists(exp):
            with open(exp, "r") as experiment_file:
                try:
                    return json.loads(experiment_file.read())
                except StandardError as err:
                    logging.error("An error was encountered while parsing the experiment JSON file '%s': %s",
                                  exp, err)
        else:
            logging.error("%s: does not exist", exp)

    def load_instance(self, instance):
        inst = os.path.join(self.get_e3_home(), "instances", "%s.json" % instance)
        if os.path.exists(inst):
            with open(inst, "r") as instance_file:
                return json.loads(instance_file.read())
        else:
            logging.error("%s: does not exist", inst)

    def load_network(self, network):
        return self.load_instance(network)

    def load_run(self, run_name):
        run = os.path.join(self.get_e3_home(), "runs", run_name, "%s.json" % run_name)
        if os.path.exists(run):
            with open(run, "r") as instance_file:
                return json.loads(instance_file.read())
        else:
            logging.error("%s: does not exist", run)

    def archive_run(self, run_name):
        run = os.path.join(self.get_e3_home(), "runs", run_name)
        destination = os.path.join(self.get_e3_home(), "archive", run_name)
        if os.path.exists(run):
            if not os.path.exists(destination):
                os.makedirs(destination)
            instance_files = self.get_run_instance_files(run_name)
            for instance_file in instance_files:
                archive_instance_file = os.path.join(run, os.path.basename(instance_file))
                if os.path.exists(instance_file):
                    os.rename(instance_file, archive_instance_file)
                    logging.debug("Archived '%s' to '%s'" % (instance_file, archive_instance_file))
            os.rename(run, destination)
            logging.info("Archived run '%s' to '%s'" % (run_name, destination))
        else:
            logging.error("%s: does not exist", run)

    @staticmethod
    def get_user_home():
        return os.path.expanduser("~")

    @staticmethod
    def get_logging_conf():
        return E3._discover_logging_file()

    @staticmethod
    def get_current_user():
        return getpass.getuser()

    @staticmethod
    def _get_stack_network(instance_stack):
        if instance_stack:
            run_conf = instance_stack.get('RunConfig', {'network': None})
            return run_conf['network']

    @staticmethod
    def _discover_logging_file():
        # Look for the logging.conf in the current working folder
        logging_conf_in_cwd = os.path.join(os.getcwd(), E3._logging_file_name)
        logging.debug("Checking if '%s' exists", logging_conf_in_cwd)
        if os.path.exists(logging_conf_in_cwd):
            return logging_conf_in_cwd
        # Look for the logging.conf file in the PYTHON_PATH
        for sys_path in sys.path:
            logging_conf_in_sys_path = os.path.join(sys_path, E3._logging_file_name)
            logging.debug("Checking if '%s' exists", logging_conf_in_sys_path)
            if os.path.exists(logging_conf_in_sys_path):
                return logging_conf_in_sys_path

    @staticmethod
    def _discover_config_file():
        # Look for the e3.yaml in the current working folder
        config_in_cwd = os.path.join(os.getcwd(), E3._config_file_name)
        logging.debug("Checking if config file '%s' exists", config_in_cwd)
        if os.path.exists(config_in_cwd):
            return config_in_cwd
        # Look for the e3.yaml file in the PYTHON_PATH
        for sys_path in sys.path:
            config_in_sys_path = os.path.join(sys_path, E3._config_file_name)
            logging.debug("Checking if config file '%s' exists", config_in_sys_path)
            if os.path.exists(config_in_sys_path):
                return config_in_sys_path

    @staticmethod
    def _read_configuration(config_in_cwd):
        with open(config_in_cwd) as e3_config:
            return yaml.load(e3_config)

e3 = E3()
