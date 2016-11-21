import os
from datetime import datetime

from TestScript import TestScript


class PushChanges(TestScript):
    def __init__(self, number, args, helper, repo_dir_pattern='%s/%s_%s'):
        super(PushChanges, self).__init__(number, args)
        self.protocol_helper = helper
        self.repo_dir_pattern = repo_dir_pattern

    @staticmethod
    def modify_files(repository, text, changes_file_count):
        files_visited = 0
        for root, dirs, files in os.walk(repository):
            if files_visited > changes_file_count:
                break
            if ".git" in dirs:
                dirs.remove(".git")
            for file in files:
                if file == ".gitignore":
                    continue
                f = open(os.path.join(root, file), "a")
                try:
                    f.write(text)
                finally:
                    f.close()
                files_visited += 1

    def add(self, cwd):
        self.run_git(["add", "."], self.runner, cwd=cwd)

    def branch(self, cwd, branch_name):
        self.run_git(["branch", branch_name], self.runner, cwd=cwd)

    def checkout(self, cwd, branch_name):
        self.run_git(["checkout", branch_name], self.runner, cwd=cwd)

    def clone(self, repo_name, branch):
        self.run_git([
            "clone", "-b", branch,
            self.protocol_helper.make_url(repo_name, self.test_data.choose_http_user_at_random()),
            self.repo_dir_pattern % ('%s/work/' % self.root, repo_name, self.get_thread_number())
        ], self.runner, env=self.protocol_helper.environment(self.test_data.choose_ssh_user_at_random()))

    def push(self, cwd, branch_name):
        self.run_git(["push", "-f", "--set-upstream", "origin", branch_name], self.runner, cwd=cwd,
                     env=self.protocol_helper.environment(self.test_data.choose_ssh_user_at_random()))

    def commit(self, cwd, message):
        self.run_git(["commit", "-m", message], self.runner, cwd=cwd)

    def __call__(self):
        (project, repo) = self.test_data.random_project_repo_tuple()
        if "branches" in repo:
            target_branch_name = repo["branches"][0]["displayId"]
        else:
            target_branch_name = "master"
        repo_name = self.test_data.name_of_repo(project, repo)
        repo_dir = self.repo_dir_pattern % ('%s/work/' % self.root, repo_name, self.get_thread_number())
        if not os.path.isdir(repo_dir):
            self.clone(repo_name, target_branch_name)
        now = datetime.now()
        # Python 2.5 has no %f :-(
        branch_name = "bugfix/%s.%s-%s" % (
            now.strftime("%Y-%m-%dT%H.%M.%S"), now.microsecond, self.get_thread_number())
        self.branch(repo_dir, branch_name)
        self.checkout(repo_dir, branch_name)
        self.modify_files(repo_dir, "foo\n", 1)
        self.add(repo_dir)
        self.commit(repo_dir, "do it")
        self.push(repo_dir, branch_name)
