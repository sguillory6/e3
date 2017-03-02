import os
import utils

from java.lang import System
from org.slf4j import LoggerFactory


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
                                 "instance file %s located in %s/e3/data/instances or %s/instances" % (
                                 instance_json_file, root, root))
        instance = utils.load_json(instance_json_file)

        self.base_url = instance["URL"]
        self.admin_password = instance["RunConfig"]["admin_password"]