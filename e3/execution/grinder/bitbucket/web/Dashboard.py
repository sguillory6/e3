from bitbucket.common.helper.Inbox import rest_get_inbox_count
from bitbucket.common.helper.Repositories import rest_get_recent_repositories
from bitbucket.common.helper.Authentication import login, logout

from Instrumentation import instrument
from TestScript import TestScript


class Dashboard(TestScript):
    def __init__(self, number, args):
        super(Dashboard, self).__init__(number, args)
        instrument()

    def __call__(self, perform_login=True):
        # Perform a login if required
        if not perform_login or login(self, self.test_data.choose_http_user_at_random()):
            # Get the Dashboard
            self.get_dashboard()
            # Load page AJAX
            rest_get_inbox_count(self)
            rest_get_recent_repositories(self)
            self.rest_get_pr_suggestions()

            if perform_login:
                # Log out
                logout(self)

    def get_dashboard(self):
        """
        Gets the dashboard for the specified user
        :return: The dashboard response as a string
        :rtype: str
        """
        return self.http("GET", "/dashboard")

    def rest_get_pr_suggestions(self):
        """
        Poll the dashboard for pull request suggestions
        :return: The JSON object for PR suggestions
        :rtype: dict
        """
        return self.rest("GET", "/rest/api/latest/dashboard/pull-request-suggestions", {
            "changesSince": "86400",
            "limit": "3",
            "avatarSize": "16"
        })
