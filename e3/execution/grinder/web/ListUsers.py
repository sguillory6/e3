from Instrumentation import instrument
from common.helper.Authentication import login
from TestScript import TestScript
from Tools import is_http_ok


class ListUsers(TestScript):
    def __init__(self, number, args):
        super(ListUsers, self).__init__(number, args)
        instrument()

    def __call__(self):
        success = 0
        if login(self, {
            "username": "admin",
            "password": self.test_data.admin_password
        }):
            self.rest("GET", "/rest/api/latest/users")
            if is_http_ok():
                success += 1

            if success == 0:
                self.report_success(False)
