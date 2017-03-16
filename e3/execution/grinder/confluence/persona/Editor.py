from confluence.common.htmlparser.MetaAttributeParser import MetaAttributeParser
from confluence.common.helper.ConfluenceUserCreator import create_user
from confluence.common.helper.Authentication import login, logout
from confluence.common.helper.ResourceUtils import *
from confluence.common.wrapper.User import User

from TestScript import TestScript

from net.grinder.script.Grinder import grinder
from org.slf4j import LoggerFactory

import re


class Editor(TestScript):
    def __init__(self, number, args):
        super(Editor, self).__init__(number, args)
        self.logger = LoggerFactory.getLogger("atlassian")
        self._current_user = None

        self._space_key = url_encode(get_space_key())
        self._pages_to_edit = get_pages_to_edit()

    def __call__(self, *args, **kwargs):
        user_name = create_user(self.test_data.base_url, grinder, "editor")
        self._current_user = User(user_name, user_name)

        if self._current_user is None:
            self.report_success(False)
            return

        login(self, self._current_user)

        self.visit_dashboard()

        run_num = grinder.getRunNumber()

        # view page
        item_num = run_num % len(self._pages_to_edit)
        page_response = self.view_page_by_title(self._pages_to_edit[item_num]["page"], self._space_key)

        page_id_meta_parser = MetaAttributeParser('ajs-page-id')
        page_id_meta_parser.feed(page_response)
        page_id_meta_parser.close()
        page_id = page_id_meta_parser.meta_content

        # edit page
        editor_response = self.edit_page(page_id)

        page_version = get_meta_attribute(editor_response, 'ajs-page-version')      # originalVersion
        parent_page_id = get_meta_attribute(editor_response, 'ajs-parent-page-id')  # parentPageString
        page_title = get_meta_attribute(editor_response, 'ajs-page-title')          # pageTitle
        space_key = get_meta_attribute(editor_response, 'ajs-space-key')            # newSpaceKey

        # get hidden syncRev attribute
        m = re.search('name="syncRev" value="(.+)"', editor_response)
        if m is None:
            self.report_success(False)
            return

        # submit page
        self.publish_page(parent_page_id,
                          "Edited by %s" % user_name, page_id, space_key, page_title,
                          str(int(page_version) + 1),
                          m.group(1))

        logout(self)

        self.report_success(True)

    def visit_dashboard(self):
        self.http("GET", "/dashboard.action#all-updates")

    def view_page_by_title(self, page_name, space_key):
        return self.http("GET", "/display/%s/%s" % (space_key, url_encode(page_name)), {"showComments": "true"})

    def edit_page(self, page_id):
        return self.http("GET", "/pages/editpage.action", {"pageId": page_id})

    def publish_page(self, parent_id, body, page_id, space_key, page_title, new_version, sync_rev):
        request_body = {"ancestors": [{"id": parent_id, "type": "page"}],
                        "body": {"editor": {"content": {"id": page_id},
                                            "representation": "editor",
                                            "value": body},
                                 "id": page_id},
                        "id": page_id,
                        "space": {"key": space_key},
                        "status": "current",
                        "title": page_title,
                        "type": "page",
                        "version": {"message": "",
                                    "minorEdit": "true",
                                    "number": new_version,
                                    "syncRev": sync_rev}}

        return self.rest("PUT", "/rest/api/content/%s" % page_id, request_body)
