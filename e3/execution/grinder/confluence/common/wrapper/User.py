import os
from exceptions import OSError
import base64
from tempfile import mkdtemp


class User(object):
    """
    User information and utilities
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return "User(username=%s)" % self.username

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __getitem__(self, item):
        """
        Keep behaviour the same as the dict() version of user
        :param item:
        :return:
        """
        if item == "username":
            return self.username
        elif item == "password":
            return self.password

        raise(KeyError("Key '%s' not found on object '%s'" % (item, self)))

    def get_env(self):
        return {
            "USER": self.username,
            "LOGNAME": self.username,
            "LANG": "en_US.UTF-8",
            "LC_COLLATE": "en_US.UTF-8",
            "LC_CTYPE": "en_US.UTF-8"
        }

    @classmethod
    def from_json(cls, j_user):
        """
        Construct a user from JSON
        :param j_user: The user json
        :type j_user: dict
        :return: A user
        :rtype: User
        """
        return cls(
            j_user.get("username", None),
            j_user.get("password", None)
        )

    @classmethod
    def from_dict(cls, d_user):
        """
        Construct a user from a TestDataProvider dictionary
        :param d_user: The user dictionary
        :type d_user: dict
        :return: A user
        :rtype: User
        """
        return cls(
            d_user.get("username", None),
            d_user.get("password", None)
        )
