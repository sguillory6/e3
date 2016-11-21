import spur
import sys
import time

from provisioning.Template import Template


class WorkerCluster(Template):
    def __init__(self, aws, e3_properties):
        stack_config = {
            "StackName": "",
            "Template": "WorkerCluster",
            "CloudFormation": {
                'InstanceType': 'c3.2xlarge',
                'KeyName': self.get_stack_name,
                'Subnets': self.get_subnets,
                'VPC': self.get_vpc,
                'ClusterSize': "4"
            },
            "Orchestration": {
                "CollectdConfig": "worker-collectd.conf",
                "StackNamePrefix": "worker",
            },
            "Output": {
                "ClusterNodes": []
            }
        }
        Template.__init__(self, aws, e3_properties, stack_config)

    def after_provision(self):
        self.wait_all_nodes_launched()
        stack_name = self._stack_config["StackName"]
        # Inject the actual public dns names of all the cluster nodes into the stack Output
        asg_name = self.get_stack_output(stack_name, 'AutoScalingGroupName')
        self._stack_config["Output"]['ClusterNodes'] = self.ssh_connection_strings_for_auto_scaling_group(asg_name)

    def before_provision(self):
        self.create_key_pair()

    def stack_public_dns_names(self):
        asg_name = self.get_stack_output(self.get_stack_name(), 'AutoScalingGroupName')
        return self.public_dns_names_for_auto_scaling_group(asg_name)

    def wait_all_nodes_launched(self):
        dns_names = self.stack_public_dns_names()
        expected_nodes = int(self._stack_config['CloudFormation']['ClusterSize'])
        while len(dns_names) != expected_nodes:
            self._log.info("Expected %d nodes launched, currently %d launched" % (expected_nodes, len(dns_names)))
            dns_names = self.stack_public_dns_names()
            time.sleep(5)
        up = 0
        while up != expected_nodes:
            up = 0
            for host_name in dns_names:
                try:
                    # Run a test SSH command on the node, if this succeeds without error then the node is ready to work.
                    self._log.debug("Attempting to ssh -i %s/%s.pem ec2-user@%s echo" % (self._e3_properties["instances_dir"], self.get_stack_name(), host_name))
                    shell = spur.SshShell(hostname=host_name,
                                          username='ec2-user',
                                          private_key_file='%s/%s.pem' % (self._e3_properties["instances_dir"], self.get_stack_name()),
                                          missing_host_key=spur.ssh.MissingHostKey.accept)
                    shell.run(['echo'], allow_error=True)
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    self._log.info("%s not ready yet (%s: %s)" % (host_name, exc_type, exc_value))
                    time.sleep(5)
                else:
                    up += 1
                    self._log.info("%s is ready (%d/%d) " % (host_name, up, expected_nodes))
