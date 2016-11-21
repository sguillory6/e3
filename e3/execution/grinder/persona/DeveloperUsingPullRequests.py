from TestScript import TestScript
from common.helper.Authentication import login, logout
from common.wrapper.User import User
from web.Dashboard import Dashboard
from web.PullRequestWorkflow import PullRequestWorkflow


class DeveloperUsingPullRequests(TestScript):
    def __init__(self, number, args):
        super(DeveloperUsingPullRequests, self).__init__(number, args)
        # Dashboard instance
        self.dashboard = Dashboard(self.number, self.args)
        # PullRequestWorkflow instance
        self.pull_request = PullRequestWorkflow(self.number, self.args)
        # Instrument modules for statistics

    def __call__(self, *args, **kwargs):
        # Ensure we clean the user's home directory
        with User.from_dict(self.test_data.choose_http_user_at_random(), self.e3_temp_dir) as me:
            login(self, me)

            # View the dashboard
            self.dashboard(False)
            # Create and merge / decline a pull request
            self.pull_request(False, me)

            logout(self)
