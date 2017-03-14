import random

from confluence.common.helper.ConfluenceUserCreator import create_user
from confluence.common.helper.Authentication import login, logout
from confluence.common.wrapper.User import User

from TestScript import TestScript

from net.grinder.script.Grinder import grinder
from org.slf4j import LoggerFactory


class Searcher(TestScript):

    def __init__(self, number, args):
        super(Searcher, self).__init__(number, args)
        self.logger = LoggerFactory.getLogger("atlassian")

        self._keyword_list = get_search_keywords()
        self._label_list = get_labels()
        self._quicknav_keyword_list = get_quick_nav_keywords()

    def __call__(self, *args, **kwargs):
        user_name = create_user(self.test_data.base_url, grinder, "searcher")
        self._current_user = User(user_name, user_name)

        login(self, self._current_user)

        random_keyword_index = random.randint(0, len(self._keyword_list) - 1)
        random_label_index = random.randint(0, len(self._label_list) - 1)
        random_quicknav_keyword_index = random.randint(0, len(self._label_list) - 1)

        self.http("GET", "/dosearchsite.action",
                  {
                      "searchQuery.queryString": self._keyword_list[random_keyword_index]["keyword"],
                      "searchQuery.spaceKey": self._keyword_list[random_keyword_index]["spacekey"],
                      "submit": "Go"
                  })

        self.http("GET", "/%s" % self._label_list[random_label_index]["label"])

        self.http("GET", "/json/contentnamesearch.action",
                  {"query": self._quicknav_keyword_list[random_quicknav_keyword_index]["keyword"]})

        logout(self)

        self.report_success(True)
