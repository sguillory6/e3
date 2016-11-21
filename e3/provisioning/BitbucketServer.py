from provisioning.Bitbucket import Bitbucket


class BitbucketServer(Bitbucket):
    def __init__(self, aws, e3_properties):
        stack_config = {
            "StackName": "",
            "Template": "BitbucketServer",
            "CloudFormation": {
                'BitbucketProperties': e3_properties['properties'],
                'CatalinaOpts': '-Dcom.sun.management.jmxremote.port=3333 '
                                '-Dcom.sun.management.jmxremote.ssl=false '
                                '-Dcom.sun.management.jmxremote.authenticate=false',
                'InstanceType': 'm4.xlarge',
                'HomeVolumeType': 'Provisioned IOPS',
                'HomeIops': '3000',
                'RootIops': '1500',
                'RootVolumeType': 'Provisioned IOPS',
                'KeyName': self.get_stack_name,
                'Subnet': self.get_subnet1,
                'StartCollectd': 'true',
                'VPC': self.get_vpc,
                'HomeVolumeSnapshotId': self.find_ebs_snapshot,
                'AssociatePublicIpAddress': str(e3_properties['public']).lower()
            },
            "Orchestration": {
                "CollectdConfig": "bitbucket-collectd.conf",
                "StackNamePrefix": "bitbucket-server"
            },
            "Output": {
                "ClusterNodes": []
            }
        }
        Bitbucket.__init__(self, aws, e3_properties, stack_config)

    def after_provision(self):
        stack_name = self._stack_config["StackName"]
        self.wait_bitbucket_start(stack_name)
        self.enable_profile_logging()
        self.print_instance_info()
        # Inject the actual SSH connection string of the instance into the stack Output
        self._stack_config["Output"]['ClusterNodes'] = ['ec2-user@' + self.get_stack_output(stack_name, 'PublicIp')]

    def before_provision(self):
        self.create_key_pair()

    def print_instance_info(self):
        ip = self.get_ip()
        key_file = self._stack_config["Output"]["KeyFile"]
        self._log.info("Instance [ %s ] is ready" % self._stack_config["StackName"])
        self._log.info("Connection string: ssh -i %s ec2-user@%s" % (key_file, ip))
        self._log.info("Home folder = [ /var/atlassian/application-data/bitbucket/ ]")
        self._log.info("View log = [ ssh -i %s ec2-user@%s "
                       "'tail -F /var/atlassian/application-data/bitbucket/log/atlassian-bitbucket.log' ]" %
                       (key_file, ip))

    def get_ip(self):
        if self._e3_properties['public']:
            ip = self._stack_config["Output"]["PublicIp"]
        else:
            ip = self._stack_config["Output"]["PrivateIp"]
        return ip
