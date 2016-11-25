from common.E3 import e3
from provisioning.Bitbucket import Bitbucket
import os


class BitbucketDataCenter(Bitbucket):
    def __init__(self, aws, e3_properties, template="BitbucketDataCenter"):
        stack_config = {
            "StackName": "",
            "Template": template,
            "CloudFormation": {
                'AssociatePublicIpAddress': str(e3_properties['public']).lower(),
                'BitbucketProperties': e3_properties['properties'],
                'CatalinaOpts': '-Dcom.sun.management.jmxremote.port=3333 -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false',
                'ClusterNodeInstanceType': 'c3.xlarge',
                "CidrBlock": '0.0.0.0/0',
                'DBMasterUserPassword': 'stash3last1c',
                'DBPassword': 'stash',
                'CreateBucket': 'false',
                'ExternalSubnets': self.get_subnets,
                'InternalSubnets': self.get_subnets,
                'KeyName': self.get_stack_name,
                'StartCollectd': 'true',
                'VPC': self.get_vpc,
                'AMIOpts': 'ATL_FORCE_HOST_NAME=true'
            },
            "Orchestration": {
                "CollectdConfig": "bitbucket-collectd.conf",
                "StackNamePrefix": "bitbucket-data-center"
            },
            "Output": {
                "ClusterNodes": []
            }
        }
        Bitbucket.__init__(self, aws, e3_properties, stack_config)

    def after_provision(self):
        stack_name = self._stack_config["StackName"]

        self.wait_bitbucket_start(stack_name)
        file_server = self._stack_config['Output']['FileServer']
        self.enable_profile_logging()
        self.print_instance_info(file_server)
        # Inject the actual SSH connection strings of all the cluster nodes and file server into the stack Output
        asg_name = self.get_stack_output(stack_name, 'ClusterNodeGroup')
        self._stack_config["Output"]['ClusterNodes'] = self.ssh_connection_strings_for_auto_scaling_group(asg_name)
        self._stack_config['Output']['FileServerConnectionString'] = 'ec2-user@' + file_server

    def before_provision(self):
        self.create_key_pair()
        self.add_snapshots()
        self.add_es_bucket()

    def add_es_bucket(self):
        config = self._stack_config['CloudFormation']
        config['ESBucketName'] = self.get_es_bucket_name()

    def add_snapshots(self):
        if self._e3_properties['snapshot']:
            snapshot_file_path = os.path.join(e3.get_e3_home(), 'snapshots', self._e3_properties['snapshot'] + ".json")
            if os.path.isfile("%s" % snapshot_file_path):
                config = self._stack_config['CloudFormation']
                config['HomeVolumeSnapshotId'] = self.get_ebs_snapshot_id(self._e3_properties['snapshot'])
                config['DBSnapshotId'] = self.get_rds_snapshot_id(self._e3_properties['snapshot'])
                config['ESSnapshotId'] = self.get_es_snapshot_id(self._e3_properties['snapshot'])
            else:
                raise Exception("Snapshot file '%s' does not exist" % snapshot_file_path)

    def print_instance_info(self, file_server):
        self._log.info("Instance [ %s ] is ready" % self._stack_config["StackName"])
        key_file = self._stack_config["Output"]["KeyFile"]
        for node in self._stack_config["Output"]['ClusterNodes']:
            self._log.info("Cluster node connection string: ssh -i %s ec2-user@%s" % (key_file, node))
        self._log.info("File server connection string: ssh -i %s ec2-user@%s" % (key_file, file_server))
