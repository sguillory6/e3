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


class Searcher(TestScript):

    def __init__(self, number, args):
        super(Searcher, self).__init__(number, args)
        self.logger = LoggerFactory.getLogger("atlassian")
        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/keywords.csv"))
        with open(csv_file_path) as csv_file:
            keywords = csv.DictReader(csv_file)
            self._keyword_list = list(keywords)

        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/labels.csv"))
        with open(csv_file_path) as csv_file:
            labels = csv.DictReader(csv_file)
            self._label_list = list(labels)

        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/quicknavkeywords.csv"))
        with open(csv_file_path) as csv_file:
            quicknavkeywords = csv.DictReader(csv_file)
            self._quicknav_keyword_list = list(quicknavkeywords)

    def __call__(self, *args, **kwargs):
        agent_number = grinder.getAgentNumber()
        process_number = grinder.getProcessNumber()
        base_url = self.test_data.base_url
        thread_num = grinder.getThreadNumber()
        run_num = grinder.getRunNumber()
        user_name = "searcher%d%d%d%d" % (agent_number, process_number, thread_num, run_num)
        create_new_user(base_url, user_name, "searcher-group")
        self._current_user = User(user_name, user_name)

        login(self, self._current_user)

        random_keyword_index = random.randint(0, len(self._keyword_list) - 1)
        random_label_index = random.randint(0, len(self._label_list) - 1)
        random_quicknav_keyword_index = random.randint(0, len(self._label_list) - 1)

        self.http("GET", "/dosearchsite.action",
                  {
                      "searchQuery.queryString": self._keyword_list[random_keyword_index]["keyword"],
                      "searchQuery.spaceKey": self._keyword_list[random_keyword_index]["spacekey"],
                      "submit" : "Go"
                   })

        self.http("GET", "/%s" % self._label_list[random_label_index]["label"])

        self.http("GET", "/json/contentnamesearch.action",
                  {"query": self._quicknav_keyword_list[random_quicknav_keyword_index]["keyword"]})

        logout(self)
        self.report_success(True)
