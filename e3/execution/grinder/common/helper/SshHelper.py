from TestDataProvider import TestDataProvider


class SshHelper:
    def __init__(self):
        self.test_data = TestDataProvider()

    def choose_user_at_random(self):
        return self.test_data.choose_ssh_user_at_random()

    @staticmethod
    def make_url(repo, ignored):
        base_url = TestDataProvider().base_url
        if ":" in base_url:
            base_url = base_url.split(':')[1].replace('/', '')

        url = "ssh://%s:7999/%s.git" % (base_url, repo)
        url_parts = url.split("://")
        url_parts[1] = "git@" + url_parts[1]
        url = "://".join(url_parts)
        return url

    def environment(self, username):
        return {
            'GIT_SSH_COMMAND': "ssh -i '%s' -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
                               % self.test_data.key_file_path(username)
        }
