import os
import csv
import random

from confluence.common.htmlparser.MetaAttributeParser import MetaAttributeParser
from confluence.common.helper.ConfluenceUserCreator import create_new_user
from confluence.common.helper.Authentication import login, logout
from confluence.common.wrapper.User import User

from TestScript import TestScript

from net.grinder.script.Grinder import grinder
from org.slf4j import LoggerFactory


class Creator(TestScript):

    def __init__(self, number, args):
        super(Commentor, self).__init__(number, args)

    def __call__(self, *args, **kwargs):
        agent_number = grinder.getAgentNumber()
        process_number = grinder.getProcessNumber()
        base_url = self.test_data.base_url
        thread_num = grinder.getThreadNumber()
        run_num = grinder.getRunNumber()
        user_name = "creator%d%d%d%d" % (agent_number, process_number, thread_num, run_num)
        create_new_user(base_url, user_name, "creator-group")
        self._current_user = User(user_name, user_name)

