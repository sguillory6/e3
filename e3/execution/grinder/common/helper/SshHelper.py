from TestDataProvider import TestDataProvider
from common.helper.ProtocolHelper import ProtocolHelper


class SshHelper(ProtocolHelper):
    def __init__(self):
        test_data = TestDataProvider()
        super(SshHelper, self).__init__(test_data, test_data.choose_ssh_user_at_random())

    def make_url(self, repo):
        base_url = self.base_url
        if ":" in base_url:
            base_url = base_url.split(':')[1].replace('/', '')

        url = "ssh://%s:7999/%s.git" % (base_url, repo)
        url_parts = url.split("://")
        url_parts[1] = "git@" + url_parts[1]
        url = "://".join(url_parts)
        return url
