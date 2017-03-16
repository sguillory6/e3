import random

from confluence.common.htmlparser.MetaAttributeParser import MetaAttributeParser
from confluence.common.helper.ConfluenceUserCreator import create_user
from confluence.common.helper.Authentication import login, logout
from confluence.common.helper.ResourceUtils import *
from confluence.common.wrapper.User import User

from TestScript import TestScript

from net.grinder.script.Grinder import grinder
from org.slf4j import LoggerFactory


class Commentor(TestScript):

    def __init__(self, number, args):
        super(Commentor, self).__init__(number, args)
        self.logger = LoggerFactory.getLogger("atlassian")

        self._commented_page_list = get_pages_to_comment()
        self._comments = get_sample_comments()

    def __call__(self, *args, **kwargs):
        user_name = create_user(self.test_data.base_url, grinder, "commentor")
        self._current_user = User(user_name, user_name)

        random_page_index = random.randint(0, len(self._commented_page_list) - 1)
        random_comment_index = random.randint(0, len(self._comments) - 1)
        page = self._commented_page_list[random_page_index]["page"]
        comment = self._comments[random_comment_index]
        grinder.logger.info("Page [%s] and comment %s" % (page, random_comment_index))

        login(self, self._current_user)

        page_response = self.http("GET", page)
        page_id = get_meta_attribute(page_response, 'ajs-page-id')
        page_xsrf_token = get_meta_attribute(page_response, 'ajs-atl-token')

        grinder.logger.info("Page xsrf token [%s]" % page_xsrf_token)
        grinder.logger.info("Page id [%s]" % page_id)
        comment_form_data = {
            "atl_token": page_xsrf_token,
            "wysiwygContent": "<p>Comment from User %s</p>: %s" % (user_name, comment['value']),
            "parentId": "0"
        }

        self.http("POST", "/pages/doaddcomment.action?pageId=%s" % page_id, comment_form_data)
        self.http("GET", page, {"showComments": "true"})
        logout(self)
        self.report_success(True)
