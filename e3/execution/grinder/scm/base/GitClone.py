import shutil
import sys
import tempfile

from TestScript import TestScript


class GitClone(TestScript):
    def __init__(self, number, args, helper):
        super(GitClone, self).__init__(number, args)
        self.protocol_helper = helper
        self.username = self.protocol_helper.choose_user_at_random()

    def __call__(self):
        repo = self.test_data.random_project_repo_slug()
        url = self.protocol_helper.make_url(repo, self.username)

        temp_dir = tempfile.mkdtemp(dir=self.e3_temp_dir)
        try:
            self.run_git(["clone", url, temp_dir], self.runner, env=self.protocol_helper.environment(self.username))
        finally:
            try:
                shutil.rmtree(temp_dir)
            except OSError:
                sys.exc_clear()
