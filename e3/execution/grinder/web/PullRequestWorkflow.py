import os
import random
from datetime import datetime

import traceback

import sys
from common.helper.Authentication import login, logout
from Instrumentation import instrument
from common.helper.Repositories import browse_repository, rest_get_repository
from TestScript import TestScript
from Tools import get_http_clone_url
from common.CodeEditor import CodeEditor
from common.RandomWords import RandomWords
from common.RepositoryCache import RepositoryCache
from common.wrapper.User import User
from common.helper.Branches import rest_get_branches, get_branch_by_id, rest_get_default_branch
from common.helper.Diff import view_diff
from common.helper.PullRequests import create_pull_request, rest_get_pr_changes, rest_get_pr_diff, \
    merge_pr, get_pr_list, rest_get_pr_by_id, decline_pr


class PullRequestWorkflow(TestScript):
    def __init__(self, number, args):
        super(PullRequestWorkflow, self).__init__(number, args)
        # Construct the Repository cache
        self.cache = RepositoryCache(os.path.join(self.root, "repo_cache"))
        # Construct the random words generator
        self.words = RandomWords()
        instrument()

    def __call__(self, perform_login=True, user=None):
        try:
            with user if user else User.from_dict(self.test_data.choose_http_user_at_random(), self.e3_temp_dir) as me:
                # Perform a login if required
                if not perform_login or login(self, me):
                    # Choose the repo to work in
                    project_key, repo_slug = self.choose_working_repository()
                    clone_url = get_http_clone_url(self.test_data.base_url, me, project_key, repo_slug)
                    starting_repo = self.get_from_cache(me, clone_url)

                    working_dir = self.clone_repository(clone_url, me, starting_repo)
                    self.checkout_master_and_pull(me, working_dir)

                    # create pr
                    from_branch, to_branch = self.create_feature_branch(me, project_key, repo_slug, working_dir)
                    title = self.words.random_sentence(3)
                    description = self.words.random_sentence(10)
                    pr_id = self.create_pr(project_key, repo_slug, from_branch, to_branch, title, description)

                    if pr_id:
                        # view the diff
                        self.view_random_file_diffs(pr_id, project_key, repo_slug)

                        get_pr_list(self, project_key, repo_slug)

                        # Merge the PR
                        pr_to_merge = rest_get_pr_by_id(self, project_key, repo_slug, pr_id)
                        if not merge_pr(self, project_key, repo_slug, from_branch.identifier,
                                        pr_id, pr_to_merge["version"]):
                            self.warn("Unable to merge PR, declining it")
                            pr_to_decline = rest_get_pr_by_id(self, project_key, repo_slug, pr_id)
                            if decline_pr(self, project_key, repo_slug, pr_id, pr_to_decline["version"]):
                                self.report_success(True)
                            else:
                                self.warn("PR not merged nor declined!")
                                self.report_success(False)
                        else:
                            # Done
                            self.report_success(True)

                    if perform_login:
                        # Log out
                        logout(self)
                else:
                    self.error("Unable to log in, aborting...")
                    self.report_success(False)
        except StandardError as ex:
            traceback.print_exc(file=sys.stderr)
            self.error("Unable to execute pull request workflow: %s", ex)
            self.report_success(False)

    def view_random_file_diffs(self, pr_id, project_key, repo_slug):
        changes_in_pr = rest_get_pr_changes(self, project_key, repo_slug, pr_id)
        files_changed_in_pr = [str(change["path"]["toString"]) for change in changes_in_pr['values']]
        for _ in range(1, random.randint(1, len(files_changed_in_pr))):
            changed_file = random.choice(files_changed_in_pr)
            rest_get_pr_diff(self, project_key, repo_slug, pr_id, changed_file)

    def create_feature_branch(self, me, project_key, repo_slug, working_dir):
        # create branch, edit, add, commit and push
        feature_branch = self.create_branch_edit_files_push_to_repo(me, working_dir)
        branches = rest_get_branches(self, project_key, repo_slug)
        from_branch = get_branch_by_id(branches, feature_branch)
        to_branch = rest_get_default_branch(self, project_key, repo_slug)
        return from_branch, to_branch

    def checkout_master_and_pull(self, me, working_dir):
        # Pull any changes
        self.run_git(["checkout", "master"], env=me.get_env(), cwd=working_dir)
        self.run_git(["pull"], env=me.get_env(), cwd=working_dir)

    def clone_repository(self, clone_url, me, starting_repo):
        # Clone the starting repo so we can modify it
        working_dir = me.create_temp_dir()
        working_repo_name = os.path.basename(working_dir)
        self.run_git(["clone", starting_repo, working_repo_name], env=me.get_env(), cwd=me.home_dir)
        self.configure_git_for_repo(clone_url, me, working_dir)
        return working_dir

    def configure_git_for_repo(self, clone_url, me, working_dir):
        # By default git uses the system's credential manager to store passwords.
        # To stop git from prompting for passwords we disable the git credential helper
        # with a config setting
        self.run_git(["config", "--local", "credential.helper", ""], env=me.get_env(), cwd=working_dir)
        # Set origin
        self.run_git(["remote", "set-url", "origin", clone_url], env=me.get_env(), cwd=working_dir)

    def create_pr(self, project_key, repo_slug, from_branch, to_branch,
                  title, description, reviewers=list()):
        repo = rest_get_repository(self, project_key, repo_slug)
        view_diff(self, project_key, repo_slug, from_branch, to_branch, repo.repo_id, repo.repo_id)

        pr_id = create_pull_request(self, project_key, repo_slug,
                                    from_branch.identifier,
                                    to_branch.identifier,
                                    title, description, reviewers, repo.repo_id, repo.repo_id)
        return pr_id

    def create_branch_edit_files_push_to_repo(self, me, working_dir):
        # check out master
        self.run_git(["checkout", "master"], env=me.get_env(), cwd=working_dir)

        # pull changes
        self.run_git(["pull"], env=me.get_env(), cwd=working_dir)

        # create a branch
        feature_branch = "feature/%s" % self.words.random_word()
        self.run_git(["checkout", "-b", feature_branch], env=me.get_env(), cwd=working_dir)

        # edit some code
        editor = CodeEditor.from_repository(working_dir)
        editor.randomly_edit_files(10, 30, 10, 25)

        # add, commit and push changes
        self.run_git(["add", "."], env=me.get_env(), cwd=working_dir)
        self.run_git(["commit", "-m", "Some changes at: %s" % datetime.now()], env=me.get_env(), cwd=working_dir)
        self.run_git(["push", "-u", "origin", feature_branch], env=me.get_env(), cwd=working_dir)

        return feature_branch

    def get_from_cache(self, me, clone_url):
        # Check if we have a cached copy of the external repository
        if not self.cache.is_cached(clone_url):
            # We don't so get a temp dir and clone it and put it in the cache
            tmp_clone = self.cache.get_temp_dir()
            if self.run_git(["clone", clone_url, tmp_clone], env=me.get_env()) == 0:
                self.cache.put(clone_url, tmp_clone)
            else:
                raise IOError("Unable to cache repository: %s" % clone_url)
        # Get the chosen test repository from the cache
        return self.cache.get(clone_url)

    def choose_working_repository(self):
        # Choose a random repo to operate on
        project, repo = self.test_data.random_project_repo_tuple()
        project_key = project["name"]
        repo_slug = repo["name"]

        # Check if the chosen repository is empty
        while "empty-repository-instructions" in browse_repository(self, project_key, repo_slug):
            self.warn("The randomly chosen repository is empty, choosing another...")
            project, repo = self.test_data.random_project_repo_tuple()
            project_key = project["name"]
            repo_slug = repo["name"]

        return project_key, repo_slug
