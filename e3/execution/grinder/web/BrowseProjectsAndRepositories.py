# A test script that browses projects, repositories, and branches at the HTML and REST level.

import random

from common.helper.Authentication import login
from TestScript import TestScript
from Tools import is_http_ok


class BrowseProjectsAndRepositories(TestScript):
    def __init__(self, number, args):
        super(BrowseProjectsAndRepositories, self).__init__(number, args)

    def __call__(self):
        user = self.test_data.choose_http_user_at_random()

        success = 0
        # Browse the top level projects list.
        if login(self, user):
            self.http("GET", "/projects")

            if is_http_ok():
                projects = self.rest("GET", "/rest/api/1.0/projects")
                if is_http_ok():
                    if "size" in projects and projects["size"] > 0:
                        for i in range(1, 5):
                            # Browse the repositories list for a few randomly selected projects.
                            project_index = int(random.random() * int(projects["size"]))
                            project_key = projects["values"][project_index]["key"]
                            self.http("GET", "/projects/%s/repos" % project_key)
                            repositories = self.rest("GET", "/rest/api/1.0/projects/%s/repos" % project_key)
                            if is_http_ok():
                                if "size" in repositories and repositories["size"] > 0:
                                    for j in range(1, 3):
                                        # Browse the branches list for a few randomly selected repositories.
                                        repo_index = int(random.random() * int(repositories["size"]))
                                        repo_slug = repositories["values"][repo_index]["slug"]
                                        self.http("GET", "/projects/%s/repos/%s/branches" % (project_key, repo_slug))
                                        self.rest("GET", "/rest/api/1.0/projects/%s/repos/%s/branches" %
                                                  (project_key, repo_slug))

                                        success += 1

            if success == 0:
                self.report_success(False)

            self.sleep(500)
