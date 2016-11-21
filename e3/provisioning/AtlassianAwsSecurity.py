import logging
import logging.config
import os
import subprocess
from datetime import datetime, timedelta
from pprint import pprint

from botocore.credentials import CredentialProvider, Credentials, RefreshableCredentials
from dateutil.tz import tzlocal

from common.E3 import e3


class AtlassianAwsSecurity(CredentialProvider):
    """
    This class is only used internally by Atlassian to make use of our SAML implementation for AWS authentication.
    It is included in the E3 distribution to serve as an example of how to integrate 3rd party authentication
    tools with E3
    """
    METHOD = "awstoken"
    AWS_ACCESS_KEY_ID_KEY = 'AWS_ACCESS_KEY_ID'
    AWS_SECRET_ACCESS_KEY_KEY = 'AWS_SECRET_ACCESS_KEY'
    AWS_SECURITY_TOKEN_KEY = 'AWS_SECURITY_TOKEN'

    def __init__(self, environ=None, mapping=None):
        super(AtlassianAwsSecurity, self).__init__()
        conf = e3.get_auth_config()
        logging.debug("Atlassian AWS config: %s" % conf)
        self._script = os.path.expanduser(conf.get('script', None))
        self._token_file = os.path.expanduser(conf.get('tokens', None))
        self._token_valid_for = long(conf.get('valid_for', 3600))

    def load(self):
        return RefreshableCredentials.create_from_metadata(
            metadata=self.refresh(),
            refresh_using=self.refresh,
            method=self.METHOD)

    def refresh(self):
        if not (self._script and self._token_file):
            logging.error("Unable to refresh tokens because configuration is missing")
            return None
        self._run_script()
        return self._parse_tokens()

    def _parse_tokens(self):
        if not os.path.exists(self._token_file):
            logging.error("Unable to locate '%s' unable to load AWS credentials, trying to proceed without them.",
                          self._token_file)
        else:
            with open(self._token_file) as tokens:
                expiry = datetime.now(tzlocal()) + timedelta(minutes=55)
                metadata = {
                    "expiry_time": str(expiry)
                }
                lines = tokens.readlines()
                for line in lines:
                    line_tokens = line[7:-1]
                    eq_pos = line_tokens.find("=")
                    token_key = line_tokens[0:eq_pos]
                    token_value = line_tokens[eq_pos + 1:]
                    if token_key == self.AWS_ACCESS_KEY_ID_KEY:
                        metadata["access_key"] = token_value
                    if token_key == self.AWS_SECRET_ACCESS_KEY_KEY:
                        metadata["secret_key"] = token_value
                        self._aws_secret_access_key = token_value
                    if token_key == self.AWS_SECURITY_TOKEN_KEY:
                        metadata["token"] = token_value
                        self._aws_security_token = token_value
                return metadata
        return None

    def _run_script(self):
        environ = os.environ.copy().update({
            'PATH': '/usr/local/bin:/usr/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin',
            'SHELL': '/bin/bash'
        })
        subprocess.call(self._script, shell=True, env=environ)

