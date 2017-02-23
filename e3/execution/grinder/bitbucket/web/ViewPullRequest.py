# A test script that calls the Pull Request API at the UI and REST level.

from bitbucket.common.helper.Projects import choose_project_at_random
from bitbucket.common.helper.PullRequests import choose_pull_request_at_random, rest_get_pr_diff
from bitbucket.common.helper.Repositories import choose_repository_at_random

from TestScript import TestScript
from Tools import is_http_ok
from bitbucket.common.helper.Authentication import login


class ViewPullRequest(TestScript):
    def __init__(self, number, args):
        super(ViewPullRequest, self).__init__(number, args)

    def __call__(self):
        user = self.test_data.choose_http_user_at_random()

        if login(self, user):
            repo_under_test = choose_repository_at_random(self, choose_project_at_random(self))
            proj_key = repo_under_test.project_key
            repo_slug = repo_under_test.slug
            pr_id = choose_pull_request_at_random(self, proj_key, repo_slug)
            if is_http_ok() and (pr_id is not None):
                self.http("GET", "/projects/%s/repos/%s/pull-requests/%s" % (proj_key, repo_slug, pr_id))
                if is_http_ok():
                    rest_get_pr_diff(self, proj_key, repo_slug, pr_id)