# A test script that calls the Audit API at the REST level.

from bitbucket.common.helper.Authentication import login
from bitbucket.common.helper.Repositories import choose_repository_at_random
from bitbucket.common.helper.Projects import choose_project_at_random

from TestScript import TestScript
from Tools import is_http_ok


class Audit(TestScript):
    def __init__(self, number, args):
        super(Audit, self).__init__(number, args)

    def __call__(self):
        user = self.test_data.choose_http_user_at_random()

        success = 0
        if login(self, user):
            repo_under_test = choose_repository_at_random(self, choose_project_at_random(self))
            proj_key = repo_under_test.project_key
            repo_slug = repo_under_test.slug
            self.rest("GET", "/rest/audit/1.0/projects/%s/repos/%s/events" % (proj_key, repo_slug))
            if is_http_ok():
                success += 1

            if success == 0:
                self.report_success(False)
