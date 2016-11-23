import shutil
import sys
import tempfile

from TestScript import TestScript


class GitLsRemote(TestScript):
    def __init__(self, number, args, helper):
        super(GitLsRemote, self).__init__(number, args)
        self.protocol_helper = helper

    def __call__(self):
        repo = self.test_data.random_project_repo_slug()
        url = self.protocol_helper.make_url(repo)
        temp_dir = tempfile.mkdtemp(dir=self.root)
        try:
            self.run_git(["ls-remote", url, temp_dir], self.runner, env=self.protocol_helper.environment())
        finally:
            try:
                shutil.rmtree(temp_dir)
            except OSError:
                sys.exc_clear()
