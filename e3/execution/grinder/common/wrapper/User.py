import os
import shutil
import base64
from tempfile import mkdtemp


class User(object):
    """
    User information and utilities
    """
    def __init__(self, username, password, ssh_public_key, ssh_private_key, e3_temp_dir):
        self.username = username
        self.password = password
        self.ssh_public_key = ssh_public_key
        self.ssh_private_key = ssh_private_key
        self.home_dir = os.path.join(e3_temp_dir, base64.urlsafe_b64encode(self.username))
        self.ssh_key_path = "%s/.ssh/id_rsa" % self.home_dir

    def __repr__(self):
        return "User(username=%s)" % self.username

    def __enter__(self):
        self.create_home()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete_home()

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
        elif item == "private_key":
            return self.ssh_private_key
        elif item == "public_key":
            return self.ssh_public_key

        raise(KeyError("Key '%s' not found on object '%s'" % (item, self)))

    def get_env(self):
        return {
            "USER": self.username,
            "LOGNAME": self.username,
            "LANG": "en_US.UTF-8",
            "LC_COLLATE": "en_US.UTF-8",
            "LC_CTYPE": "en_US.UTF-8",
            "HOME": self.home_dir,
            "SHELL": "/bin/bash",
            "SSH_KEY_PATH": self.ssh_key_path,
            'GIT_SSH_COMMAND': "ssh -i '%s' -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" %
                               self.ssh_key_path
        }

    def create_home(self):
        if not os.path.exists(self.home_dir):
            os.makedirs(self.home_dir, mode=0o755)

            key_path = os.path.dirname(self.ssh_key_path)
            if not os.path.exists(key_path):
                os.makedirs(key_path, mode=0o700)

                if self.ssh_public_key and self.ssh_private_key:
                    if not os.path.exists(self.ssh_key_path):
                        with open(self.ssh_key_path, "w") as key_file:
                            key_file.write(self.ssh_private_key)
                        os.chmod(self.ssh_key_path, 0o600)

    def create_temp_dir(self):
        return mkdtemp(dir=self.home_dir)

    def delete_home(self):
        if os.path.exists(self.home_dir):
            shutil.rmtree(self.home_dir, ignore_errors=True)

    def configure_netrc(self, hostname):
        if not os.path.exists(self.home_dir):
            self.create_home()
        with open("%s/.netrc" % self.home_dir, "w") as netrc:
            netrc.write("machine %s login \"%s\" password \"%s\"" % (hostname, self.username, self.password))

    @classmethod
    def from_json(cls, j_user, e3_temp_dir):
        """
        Construct a user from JSON
        :param j_user: The user json
        :type j_user: dict
        :param e3_temp_dir: The E3 temporary directory
        :type e3_temp_dir: str
        :return: A user
        :rtype: User
        """
        return cls(
            j_user.get("username", None),
            j_user.get("password", None),
            j_user.get("ssh_key", None),
            None,
            e3_temp_dir
        )

    @classmethod
    def from_dict(cls, d_user, e3_temp_dir):
        """
        Construct a user from a TestDataProvider dictionary
        :param d_user: The user dictionary
        :type d_user: dict
        :param e3_temp_dir: The E3 temporary directory
        :type e3_temp_dir: str
        :return: A user
        :rtype: User
        """
        return cls(
            d_user.get("username", None),
            d_user.get("password", None),
            d_user.get("public_key", None),
            d_user.get("private_key", None),
            e3_temp_dir
        )
