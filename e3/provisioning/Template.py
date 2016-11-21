import binascii
import datetime
import itertools
import logging
import os
import time

from common.E3 import e3

try:
    from botocore.vendored.requests.packages.urllib3.contrib import pyopenssl

    pyopenssl.extract_from_urllib3()
except ImportError:
    pass


class Template:
    """Base class for CloudFormation templates."""
    def __init__(self, aws, e3_properties, stack_config):
        self._aws = aws
        self._e3_properties = e3_properties
        self._log = logging.getLogger('orchestrate')
        self._stack_config = stack_config
        self._stack_config["CloudFormation"].update(e3_properties['parameters'])

    @staticmethod
    def dict_to_tags(config):
        parameters = []
        for key, value in config.iteritems():
            parameters.append({"Key": key, "Value": value})
        return parameters

    # Method called by Orchestrate after the stack has been provisioned
    def after_provision(self):
        pass

    # Method called by Orchestrate before the stack has been provisioned
    def before_provision(self):
        pass

    def create_key_pair(self):
        stack_name = self._stack_config["StackName"]
        key_file = e3.get_stack_ssh_key(stack_name)
        self._stack_config["Output"]['KeyFile'] = key_file
        with open(key_file, 'w') as pem_file:
            pem_file.write(self._aws.ec2.create_key_pair(KeyName=stack_name)['KeyMaterial'])
            # Set secure permissions on file
            os.chmod(pem_file.name, 0400)
        self._log.info("PEM file for instance written to %s" % pem_file.name)
        return stack_name

    def find_ebs_snapshot(self, snapshot):
        snapshots = self._aws.ec2.describe_snapshots(Filters=[{
            'Name': 'tag:e3-dataset',
            'Values': [snapshot]
        }])['Snapshots']
        if len(snapshots) > 1:
            raise Exception("Found more than one AWS EBS snapshot with tag e3-dataset='%s'" % snapshot)
        elif len(snapshots) == 0:
            raise Exception("Could not find any AWS EBS snapshot with tag e3-dataset='%s'" % snapshot)
        snapshot_id = snapshots[0]['SnapshotId']
        self._log.info("Found EBS snapshot ID '%s' for snapshot '%s'" % (snapshot_id, snapshot))
        return snapshot_id

    def find_rds_snapshot(self, snapshot):
        """
        Finds the RDS snapshot ID from the given snapshot
        :param snapshot: the name of RDS snapshot
        :return: The RDS snapshot ID
        """
        snapshots = self._aws.rds.describe_db_snapshots(DBSnapshotIdentifier=snapshot,
                                                        IncludePublic=True)['DBSnapshots']
        if len(snapshots) > 1:
            raise Exception("Found more than one AWS RDS snapshot with name '%s'" % snapshot)
        elif len(snapshots) == 0:
            raise Exception("Could not find any AWS RDS snapshot with name '%s'" % snapshot)
        snapshot_id = snapshots[0]['DBSnapshotIdentifier']
        self._log.info("Found RDS snapshot ID '%s' for snapshot '%s'" % (snapshot_id, snapshot))
        return snapshot_id

    def validate_es_snapshot_id(self, snapshot, bucket):
        """
        Ensures that both the S3 bucket the Elasticsearch snapshot exists
        :param snapshot: the name of Elasticsearch snapshot
        :param bucket: the S3 bucket that contains the Elasticsearch snapshot
        :return: The Elasticsearch snapshot
        """
        self._log.debug("Validating Elasticsearch snapshot '%s' in S3 bucket '%s'" % (snapshot, bucket))
        if not snapshot:
            return Exception("Invalid Elasticsearch Snapshot: '%s'" % snapshot)
        if not bucket:
            raise Exception("You must specify an S3 bucket when restoring an Elasticsearch snapshot")

        self._aws.s3_client.get_object(Bucket=bucket, Key="snap-%s.dat" % snapshot)
        self._log.info("Found ES snapshot '%s' in S3 bucket '%s'" % (snapshot, bucket))
        return snapshot

    def get_es_bucket_name(self):
        if 'ESBucketName' in self._e3_properties['parameters']:
            return self._e3_properties['parameters']['ESBucketName']
        else:
            s3_bucket = e3.get_configured_es_s3_bucket()
            if s3_bucket is None:
                return ''
            else:
                return s3_bucket

    def get_stack_config(self):
        return self._stack_config

    def get_stack_name(self):
        if "StackName" in self._stack_config and len(self._stack_config["StackName"]) > 0:
            return self._stack_config["StackName"]
        else:
            name_prefix = self._stack_config["Orchestration"]["StackNamePrefix"]
            self._stack_config["StackName"] = '%s-%s-%s' % (name_prefix,
                                                            self._e3_properties['owner'],
                                                            binascii.b2a_hex(os.urandom(3)))
            return self._stack_config["StackName"]

    def get_stack_output(self, stack_name, output_key):
        return [x['OutputValue'] for x in self._aws.cloud_formation.Stack(stack_name).outputs if
                x['OutputKey'] == output_key][0]

    def get_subnet1(self):
        return self._e3_properties['subnet1']

    def get_subnet2(self):
        return self._e3_properties['subnet2']

    def get_subnets(self):
        return '%s,%s' % (self.get_subnet1(), self.get_subnet2())

    def get_vpc(self):
        return self._e3_properties['vpc']

    def generate_tags(self):
        return self.dict_to_tags({
            "Name": 'e3-' + self._stack_config["StackName"],
            "resource_owner": self._e3_properties["owner"],
            "service_name": 'e3',
            "business_unit": "Engineering-Server",
        })

    def generate_parameters(self):
        parameters = []
        for key, value in self._stack_config["CloudFormation"].iteritems():
            if callable(value):
                value = value()
            parameters.append({"ParameterKey": key, "ParameterValue": value, "UsePreviousValue": False})
        return parameters

    def public_dns_names_for_auto_scaling_group(self, asg_name):
        instances = [x['InstanceId'] for x in self._aws.auto_scaling.describe_auto_scaling_groups(
            AutoScalingGroupNames=[asg_name])['AutoScalingGroups'][0]['Instances']]
        reservations = [reservation['Instances'] for reservation in (
            self._aws.ec2.describe_instances(InstanceIds=instances)['Reservations']
        )]
        instance_list = list(itertools.chain.from_iterable(reservations))
        public_dns_names = [instance['PublicDnsName'] for instance in instance_list]
        return public_dns_names

    def ssh_connection_strings_for_auto_scaling_group(self, asg_name):
        public_dns_names = self.public_dns_names_for_auto_scaling_group(asg_name)
        return ['ec2-user@' + x for x in public_dns_names]

    def stack_status(self, stack_name):
        stack = self._aws.cloud_formation.Stack(stack_name)
        return {'status': stack.stack_status, "reason": stack.stack_status_reason}

    # boto3 doesnt support waiters on cloud formation resources yet. see https://github.com/boto/botocore/pull/630
    def wait_stack_status(self):
        stack_name = self._stack_config['StackName']
        start_time = datetime.datetime.now().replace(microsecond=0)
        stack_status = self.stack_status(stack_name)
        while stack_status['status'] == 'CREATE_IN_PROGRESS':
            self._log.info("Waiting for Stack %s to be created waited %s" % (
                stack_name, datetime.datetime.now().replace(microsecond=0) - start_time))
            time.sleep(20)
            stack_status = self.stack_status(stack_name)
        if stack_status['status'] != 'CREATE_COMPLETE':
            raise Exception(
                "Could not create stack for instance %s Reason is %s" % (
                    stack_name, stack_status['reason']))
