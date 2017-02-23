from bitbucket.common.helper import HttpHelper
from bitbucket.scm.base.GitClone import GitClone


class GitCloneOverHttp(GitClone):
    def __init__(self, number, args):
        super(GitCloneOverHttp, self).__init__(number, args, HttpHelper())
