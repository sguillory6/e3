from confluence.common.htmlparser.MetaAttributeParser import MetaAttributeParser
from confluence.common.helper.ConfluenceUserCreator import create_user
from confluence.common.helper.Authentication import login, logout
from confluence.common.helper.ResourceUtils import *
from confluence.common.wrapper.User import User

from TestScript import TestScript

from net.grinder.script.Grinder import grinder
from org.slf4j import LoggerFactory

import re

class Reader(TestScript):
    def __init__(self, number, args):
        super(Reader, self).__init__(number, args)
        self.logger = LoggerFactory.getLogger("atlassian")
        self._current_user = None

        self._space_key = url_encode(get_space_key())
        self._pages_by_title = get_pages_by_title()
        self._space_actions = get_space_actions()
        self._pages_not_found = get_pages_not_found()
        self._rss_feeds = get_rss_feed_types()
        self._oc_pages = get_oc_pages()

    def __call__(self, *args, **kwargs):
        user_name = create_user(self.test_data.base_url, grinder, "reader")
        self._current_user = User(user_name, user_name)

        if self._current_user is None:
            self.report_success(False)
            return

        login(self, self._current_user)

        self.visit_dashboard()

        run_num = grinder.getRunNumber()

        # view page
        item_num = run_num % len(self._pages_by_title)
        self.view_page_by_title(self._pages_by_title[item_num]["page"], self._space_key)

        # space action
        item_num = run_num % len(self._space_actions)
        self.view_space_action(self._space_actions[item_num]["action"], self._space_key)

        # create rss feed
        item_num = run_num % len(self._rss_feeds)
        self.create_rss_feed(self._space_key,
                             self._rss_feeds[item_num]["rss_type"],
                             self._rss_feeds[item_num]["content_type"])

        # visit pages that doesn't exist
        item_num = run_num % len(self._pages_not_found)
        self.view_page_by_title(self._pages_not_found[item_num]["page"], self._space_key)

        # view OC attachment (OC plugin should be enabled)
        item_num = run_num % len(self._oc_pages)
        self.view_office_connector_page(self._space_key, self._oc_pages[item_num])

        logout(self)

        self.report_success(True)

    def visit_dashboard(self):
        self.http("GET", "/dashboard.action#all-updates")

    def view_page_by_title(self, page_name, space_key):
        return self.http("GET", "/display/%s/%s" % (space_key, url_encode(page_name)), {"showComments": "true"})

    def view_space_action(self, action, space_key):
        self.http("GET", "/%s" % action, {"key": space_key})

    def create_rss_feed(self, space_key, rss_type, content_type):
        title = "RSS Feed"
        self.http("GET", "/spaces/createrssfeed.action", {"spaces": space_key,
                                                          "sort": "modified",
                                                          "title": url_encode(title),
                                                          "maxResults": "30",
                                                          "publicFeed": "true",
                                                          "rssType": rss_type,
                                                          "types": content_type})

    def view_office_connector_page(self, space_key, params):
        page_name = params["page_name"]
        file_name = params["file_name"]

        # get page id
        page_response = self.view_page_by_title(page_name, space_key)
        page_id_meta_parser = MetaAttributeParser('ajs-page-id')
        page_id_meta_parser.feed(page_response)
        page_id_meta_parser.close()
        page_id = page_id_meta_parser.meta_content

        if ".doc" in file_name or ".xls" in file_name:
            self.http("GET", "/pages/worddav/preview.action", {"pageId": url_encode(page_id),
                                                               "fileName": url_encode(file_name)})
        else:
            # get attachment id
            pattern = 'data-attachment="%s" data-attachment-id="([0-9]+)"' % file_name
            match = re.search(pattern, page_response)
            attachment_id = match.group(1)

            self.http("GET", "/plugins/servlet/pptslide", {"attachmentId": url_encode(attachment_id),
                                                           "attachment": url_encode(file_name),
                                                           "pageId": url_encode(page_id)})