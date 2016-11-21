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
        Utils.run_script_over_ssh(user_host, key_file, "%s/aws-generator.sh" % generator_path)
