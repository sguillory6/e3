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


class Commentor(TestScript):

    def __init__(self, number, args):
        super(Commentor, self).__init__(number, args)
        self.logger = LoggerFactory.getLogger("atlassian")
        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/pagesToComment.csv"))
        with open(csv_file_path) as csv_file:
            comment_pages = csv.DictReader(csv_file)
            self._commented_page_list = list(comment_pages)

        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources/comments.csv"))
        with open(csv_file_path) as csv_file:
            comments_reader = csv.DictReader(csv_file)
            self._comments = list(comments_reader)

    def __call__(self, *args, **kwargs):
        agent_number = grinder.getAgentNumber()
        process_number = grinder.getProcessNumber()
        base_url = self.test_data.base_url
        thread_num = grinder.getThreadNumber()
        run_num = grinder.getRunNumber()
        user_name = "commentor%d%d%d%d" % (agent_number, process_number, thread_num, run_num)
        create_new_user(base_url, user_name, "commentor-group")
        self._current_user = User(user_name, user_name)

        random_page_index = random.randint(0, len(self._commented_page_list) - 1)
        random_comment_index = random.randint(0, len(self._comments) - 1)
        page = self._commented_page_list[random_page_index]["page"]
        comment = self._comments[random_comment_index]
        grinder.logger.info("Page [%s] and comment %s" % (page, random_comment_index))

        login(self, self._current_user)

        page_response = self.http("GET", page)
        page_id_meta_parser = MetaAttributeParser('ajs-page-id')
        page_id_meta_parser.feed(page_response)
        page_id_meta_parser.close()
        page_id = page_id_meta_parser.meta_content

        page_xsrf_token_parser = MetaAttributeParser('ajs-atl-token')
        page_xsrf_token_parser.feed(page_response)
        page_xsrf_token_parser.close()
        page_xsrf_token = page_xsrf_token_parser.meta_content

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