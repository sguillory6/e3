import os
import random

from java.lang import System
from org.slf4j import LoggerFactory

import utils


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TestDataProvider:
    __metaclass__ = Singleton

    def __init__(self):
        # Ensure we don't write to the agent or worker logs
        self.logger = LoggerFactory.getLogger("atlassian")

        root = System.getProperty("root")
        instance_json_file = "%s/e3/data/instances/%s.json" % (root, System.getProperty("instance"))
        if not os.path.exists(instance_json_file):
            instance_json_file = "%s/instances/%s.json" % (root, System.getProperty("instance"))
            if not os.path.exists(instance_json_file):
                raise ValueError("Instance must be the name of a valid "
                                 "instance file located in %s/e3/data/instances or %s/instances" % (root, root))
        instance = utils.load_json(instance_json_file)

        snapshot_json_file = "%s/e3/data/snapshots/%s.json" % (root, instance["snapshot"])
        if not os.path.exists(snapshot_json_file):
            snapshot_json_file = "%s/snapshots/%s.json" % (root, instance["snapshot"])
            if not os.path.exists(instance_json_file):
                raise ValueError("Snapshot must be the name of a valid "
                                 "snapshot file located in %s/e3/data/snapshots or %s/snapshots" % (root, root))
        self.snapshot = utils.load_json(snapshot_json_file)

        self.base_url = instance["URL"]
        self.admin_password = instance["RunConfig"]["admin_password"]

        self.total_repo_weight = self.sum_of_repo_weights()
        self.http_auth_users = []
        self.ssh_auth_users = []
        for user in self.snapshot['users']:
            if 'private_key' not in user and 'password' not in user:
                self.logger.warn("Could not find any credentials for user %s" % user)
                continue

            if 'password' in user:
                self.http_auth_users.append(user)

            if 'private_key' in user:
                self.ssh_auth_users.append(user)

    def random_project_repo_tuple(self):
        weight = random.random() * self.total_repo_weight
        project = None
        repo = None
        for project in self.snapshot["projects"]:
            for repo in project["repos"]:
                weight -= repo["weight"]
                if weight <= 0:
                    return project, repo
        if project is None or repo is None:
            raise Exception("Could not find either project or repo to run test against")
        return project, repo

    def random_project_repo_slug(self):
        project, repo = self.random_project_repo_tuple()
        return self.name_of_repo(project, repo)

    def choose_http_user_at_random(self):
        return random.choice(self.http_auth_users)

    def choose_ssh_user_at_random(self):
        return random.choice(self.ssh_auth_users)

    def sum_of_repo_weights(self):
        total_weight = 0.0
        for project in self.snapshot["projects"]:
            for repo in project["repos"]:
                total_weight += repo["weight"]
        return total_weight

    @staticmethod
    def name_of_repo(project, repo):
        return "%s/%s" % (project["name"], repo["name"])
