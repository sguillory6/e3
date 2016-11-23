import os
from java.lang import System
from common.wrapper.User import User


class ProtocolHelper(object):
    def __init__(self, test_data, user_dict):
        self.base_url = test_data.base_url
        self.user = User.from_dict(user_dict, os.path.join(System.getProperty("root"), "tmp"))
        self.user.create_home()

    def environment(self):
        return self.user.get_env()
