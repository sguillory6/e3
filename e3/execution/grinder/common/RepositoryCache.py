import base64
import os
import shutil
from tempfile import mkdtemp


class RepositoryCache:
    """
    Used to cache cloned repositories
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def get(self, repository_name):
        """
        Gets a repository from the cache
        :param repository_name: The name or url of the repository to get
        :type repository_name: str
        :return: The cached repository or None
        :rtype: str
        """
        encoded_name = base64.urlsafe_b64encode(repository_name)
        maybe_cached = os.path.join(self.base_dir, encoded_name)
        if os.path.exists(maybe_cached):
            return maybe_cached

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

        encoded_name = base64.urlsafe_b64encode(repository_name)
        dest_dir = os.path.join(self.base_dir, encoded_name)

        try:
            os.rename(location, dest_dir)
        except OSError as ex:
            if "Directory not empty" in ex:
                shutil.rmtree(location)
            else:
                raise

        return dest_dir

    def get_temp_dir(self):
        """
        Get a temporary folder in the cache, which is exclusive to the caller.
        It is used to place data into the cache
        :return: the temp directory
        :rtype: str
        """
        return mkdtemp(dir=self.base_dir)
