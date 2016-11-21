from TestDataProvider import TestDataProvider


class HttpDirectHelper:
    def __init__(self):
        self.test_data = TestDataProvider()

    def choose_user_at_random(self):
        return self.test_data.choose_http_user_at_random()

    def make_url(self, repo, user):
        url = self.test_data.base_url
        if ':7990' not in url:
            url += '7990'

        url_parts = url.split("://")
        url_parts[1] = user['username'] + ":" + user['password'] + "@" + url_parts[1]
        url = "://".join(url_parts)

        return "%s/scm/%s.git" % (url, repo)

    @staticmethod
    def environment(ignore):
        return {}
