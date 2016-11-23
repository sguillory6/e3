import urllib
from TestDataProvider import TestDataProvider
from common.helper.ProtocolHelper import ProtocolHelper


class HttpDirectHelper(ProtocolHelper):
    def __init__(self):
        test_data = TestDataProvider()
        super(HttpDirectHelper, self).__init__(test_data, test_data.choose_http_user_at_random())

    def make_url(self, repo):
        url = self.base_url
        if ':7990' not in url:
            url += '7990'

        url_parts = url.split("://")
        username = urllib.urlencode(self.user['username'])
        password = urllib.urlencode(self.user['password'])
        url_parts[1] = username + ":" + password + "@" + url_parts[1]
        url = "://".join(url_parts)

        return "%s/scm/%s.git" % (url, repo)
