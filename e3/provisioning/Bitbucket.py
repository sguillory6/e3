import re
import requests
from requests import ConnectionError

from common import Utils
from provisioning.Template import Template


class Bitbucket(Template):
    _admin_password = None

    def __init__(self, aws, e3_properties, stack_config):
        if "version" in e3_properties:
            stack_config["CloudFormation"]["BitbucketVersion"] = e3_properties["version"]

        if len(stack_config["CloudFormation"]["BitbucketProperties"]) > 0:
            stack_config["CloudFormation"]["BitbucketProperties"] += ","
        stack_config["CloudFormation"]["BitbucketProperties"] += "jmx.enabled=true"

        self._admin_password = e3_properties['admin_password']
        Template.__init__(self, aws, e3_properties, stack_config)

    def enable_profile_logging(self):
        self._log.info("Attempting to enable profile logging with username:%s and password %s" %
                       ("admin", self._admin_password))
        try:
            stack_name = self._stack_config["StackName"]
            profiling_admin = self.get_stack_output(stack_name, 'URL') + "/admin/profiling"
            requests.post(profiling_admin, json={"enabled": "true"}, auth=('admin', '3last1c'))
        except ConnectionError as ce:
            self._log.error('''
            A connection error occurred while enabling profile logging,
            this could mean that Bitbucket did not start correctly
            [%s]
            ''', ce)
        except AttributeError as e:
            self._log.error("Could not enable profile logging error [%s]" % e)

    def wait_bitbucket_start(self, stack_name):
        status_url = self.get_stack_output(stack_name, 'URL') + '/status'
        return Utils.poll_url(status_url, 900, lambda response: response.text == '{"state":"RUNNING"}')

    def post_with_security_info(self, path, data):
        url = self.get_stack_output(self._stack_config["StackName"], 'URL') + path
        security = self.get_security_info(url)
        data['atl_token'] = security['atl_token']
        try:
            r = requests.post(url, data=data, auth=('admin', self._admin_password),
                              headers={"Cookie": security['j_session_id']})
        except requests.exceptions.RequestException as e:
            self._log.error(e)

    def get_security_info(self, url):
        # Authenticate and get response
        response = requests.get(url, auth=('admin', self._admin_password))

        # Parse HTML for atl_token
        atl_token = re.search("atl_token.*value=\"(.*?)\"", response.text).group(1)

        # Parse response headers for JSESSIONID
        j_session_id = response.headers['Set-Cookie'].split(" ")[0]

        return {'atl_token': atl_token, 'j_session_id': j_session_id}
