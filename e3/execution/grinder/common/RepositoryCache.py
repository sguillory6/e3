import os
from tempfile import mkdtemp

from FileLock import FileLock
from utils import load_json, save_json


class RepositoryCache:
    """
    Used to cache cloned repositories
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.cache_lock = FileLock(base_dir, "cache")
        self.CACHE_DB = os.path.join(self.base_dir, "cache.json")

    def list(self):
        """
        Get the names for cached repositories
        :return: repositories or None
        :rtype: list(str)
        """
        with self.cache_lock:
            if not os.path.exists(self.CACHE_DB):
                return []
            cache = load_json(self.CACHE_DB)
            return map(lambda entry: entry["name"], cache["repositories"])

    def get(self, repo_name):
        """
        Gets a repository from the cache
        :param repo_name: The name or url of the repository to get
        :type repo_name: str
        :return: The cached repository or None
        :rtype: str
        """
        with self.cache_lock:
            if not os.path.exists(self.CACHE_DB):
                return None
            found = None
            cache = load_json(self.CACHE_DB)
            for repo in cache["repositories"]:
                if repo["name"] == repo_name:
                    found = repo
                    break
            if found:
                return found["directory"]

            return found

    def put(self, repository_name, location):
        """
        Puts a repository into the cache
        :param repository_name: The key to use for this repository
        :type repository_name: str
        :param location: The directory containing the repository,
                         most often the same as the directory returned from get_temp_dir
        :type location: str
        :return: The cached repository location
        :rtype: str
        """
        if not os.path.abspath(location).startswith(os.path.abspath(self.base_dir)):
            raise ValueError("The temp folder is not a sub folder of the base folder")

        with self.cache_lock:
            if not os.path.exists(self.CACHE_DB):
                cache = {"repositories": []}
            else:
                cache = load_json(self.CACHE_DB)

            repo_dir = os.path.abspath(location)

            cache["repositories"].append({
                "name": repository_name,
                "directory": repo_dir
            })

            save_json(self.CACHE_DB, cache)

            return repo_dir

    def get_temp_dir(self):
        """
        Get a temporary folder in the cache, which is exclusive to the caller.
        It is used to place data into the cache
        :return: the temp directory
        :rtype: str
        """
        return mkdtemp(dir=self.base_dir)
