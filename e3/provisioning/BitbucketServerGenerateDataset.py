import spur
from common import Utils
from provisioning.BitbucketServer import BitbucketServer


class BitbucketServerGenerateDataSet(BitbucketServer):
    def __init__(self, aws, e3_properties):
        BitbucketServer.__init__(self, aws, e3_properties)
        self._stack_config["Orchestration"]["StackNamePrefix"] = "generate-dataset"

    def after_provision(self):
        user_host = 'ec2-user@' + self.get_ip()
        key_file = self._stack_config["Output"]["KeyFile"]

        print "Copying test-data-generator files"
        generator_path = '/home/ec2-user/generator'
        Utils.rsync(user_host, key_file, generator_path, "../generator/")
        shell = spur.SshShell(
            hostname=self.get_ip(),
            username="ec2-user",
            private_key_file=key_file,
            missing_host_key=spur.ssh.MissingHostKey.accept,
            connect_timeout=3600
        )
        shell.run("%s/aws-generator.sh" % generator_path)
