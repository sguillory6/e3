import random, string

from confluence.common.htmlparser.MetaAttributeParser import MetaAttributeParser
from confluence.common.helper.ConfluenceUserCreator import create_user
from confluence.common.helper.Authentication import login, logout
from confluence.common.helper.ResourceUtils import *
from confluence.common.wrapper.User import User

from TestScript import TestScript

from net.grinder.script.Grinder import grinder


class Creator(TestScript):
    def __init__(self, number, args):
        super(Creator, self).__init__(number, args)
        self._sample_page_text = get_page_sample_text()

    def __call__(self, *args, **kwargs):
        user_name = create_user(self.test_data.base_url, grinder, "creator")
        rand_str = lambda n: ''.join([random.choice(string.lowercase) for i in xrange(n)])
        self._current_user = User(user_name, user_name)
        space_key = "ds"
        page_title = "Creator page %s" % rand_str(15)
        random_page_index = random.randint(0, len(self._sample_page_text) - 1)

        login(self, self._current_user)

        response = self.http("GET", "/pages/createpage.action?spaceKey=%s" % space_key)
        if not response:
            self.report_success(False)
            return

        page_xsrf_token_parser = MetaAttributeParser('ajs-atl-token')
        page_xsrf_token_parser.feed(response)
        page_xsrf_token_parser.close()
        page_xsrf_token = page_xsrf_token_parser.meta_content

        response = self.http("GET", "/plugins/macrobrowser/browse-macros.action")
        if not response:
            self.report_success(False)
            return

        page_create_form = {
            "atl_token": page_xsrf_token,
            "fromPageId": "0",
            "labelsShowing": "false",
            "restrictionsShowing": "false",
            "locationShowing": "false",
            "spaceKey": space_key,
            "titleWritten": "false",
            "linkCreation": "false",
            "title": page_title,
            "confirm": "save",
            "useWysiwyg": "false",
            "saveDrafts": "true",
            "draftType": "page",
            "heartbeat": "true",
            "newPage": "true",
            "formName": "createpageform",
            "content": self._sample_page_text[random_page_index]["pageText"],
            "mode": "markup",
            "inPreview": "false",
            "xhtml": "false",
            "newSpaceKey": space_key,
            "labelsString": "performance tesing"
        }
        self.http("POST", "/pages/docreatepage.action?dummy=abc&querystr=1", page_create_form)

        self.http("GET", "/display/%s/%s" % (space_key, url_encode(page_title)))

        logout(self)

        self.report_success(True)
