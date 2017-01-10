from provisioning.Template import Template
from common import Utils


class ConfluenceDataCenter(Template):
    def __init__(self, aws, e3_properties, template="ConfluenceDataCenter"):
        stack_config = {
            "StackName": "",
            "Template": template,
            "CloudFormation": {
                'AssociatePublicIpAddress': str(e3_properties['public']).lower(),
                'CatalinaOpts': '-Dcom.sun.management.jmxremote.port=3333 -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false',
                'ConfluenceVersion': '6.1.0-m09',
                'ClusterNodeInstanceType': 'c3.xlarge',
                "CidrBlock": '0.0.0.0/0',
                'DBMasterUserPassword': 'conf3last1c',
                'DBPassword': 'confluence',
                'ExternalSubnets': self.get_subnets,
                'InternalSubnets': self.get_subnets,
                'KeyName': self.get_stack_name,
                'StartCollectd': 'true',
                'VPC': self.get_vpc,
            },
            "Orchestration": {
                "CollectdConfig": "confluence-collectd.conf",
                "StackNamePrefix": "confluence-data-center"
            },
            "Output": {
                "ClusterNodes": []
            }
        }
        Template.__init__(self, aws, e3_properties, stack_config)

    def after_provision(self):
        stack_name = self._stack_config["StackName"]
        asg_name = self.get_stack_output(stack_name, 'ClusterNodeGroup')
        ssg_name = self.get_stack_output(stack_name, 'SynchronyClusterNodeGroup')
        self._stack_config["Output"]['ClusterNodes'] = self.ssh_connection_strings_for_auto_scaling_group(asg_name)
        self.wait_confluence_start(stack_name)
        # write provision information into properties file.
        # Will easier to to export provisioning metadata into bamboo variables
        try:
            fo = open("target\confluence-provision.properties", "wb")
            for item in self._stack_config["Output"]:
                fo.writelines("%s=%s" % (item, self._stack_config["Output"][item]))
        except IOError:
            self._log.error("Could not write confluence-provision.properties")
        else:
            fo.close()

    def before_provision(self):
        # should check if we have a key pair already
        self.create_key_pair()

    def wait_confluence_start(self, stack_name):
        status_url = self.get_stack_output(stack_name, 'URL') + '/status'
        return Utils.poll_url(
            status_url,
            900,
            lambda response: response.text == '{"state":"RUNNING"}' or response.text == '{"state":"FIRST_RUN"}'
        )
