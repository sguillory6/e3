from confluence.common.helper.ConfluenceUserCreator import create_new_user
from confluence.common.helper.Authentication import login, logout
from confluence.common.wrapper.User import User

from TestScript import TestScript

from java.lang import System
from net.grinder.script.Grinder import grinder
from org.slf4j import LoggerFactory


class Reader(TestScript):
    def __init__(self, number, args):
        super(Reader, self).__init__(number, args)
        self.logger = LoggerFactory.getLogger("atlassian")
        process_count_per_agent = grinder.getProperties().getDouble("grinder.processes", 1.0)
        thread_count_per_process = grinder.getProperties().getDouble("grinder.threads", 1.0)
        agent_count = float(System.getProperty("agentCount"))
        base_url = self.test_data.base_url
        user_name = "reader%d%d%d" %(agent_count, process_count_per_agent, thread_count_per_process)
        create_new_user(base_url, user_name, "reader-group")
        self._current_user = User(user_name, user_name)

    def __call__(self, *args, **kwargs):
        login(self, self._current_user)
        # go to dashboard
        self.http("GET", "/dashboard.action#all-updates")
        logout(self)


