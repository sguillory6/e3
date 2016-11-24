# A test script that calls the Pull Request API at the REST level.

from common.helper.Authentication import login
from TestScript import TestScript
from Tools import is_http_ok

from Instrumentation import instrument
from common.helper.Projects import choose_project_at_random
from common.helper.Repositories import choose_repository_at_random
from common.helper.PullRequests import rest_get_pr_list


class ListPullRequests(TestScript):
    def __init__(self, number, args):
        super(ListPullRequests, self).__init__(number, args)
        instrument()

    def __call__(self):
        user = self.test_data.choose_http_user_at_random()

        success = 0
        if login(self, user):
            repo_under_test = choose_repository_at_random(self, choose_project_at_random(self))
            rest_get_pr_list(self, repo_under_test.project_key, repo_under_test.slug)
            if is_http_ok():
                success += 1

            if success == 0:
                self.report_success(False)
