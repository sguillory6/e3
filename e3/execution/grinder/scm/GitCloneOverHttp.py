from scm.base.GitClone import GitClone
from common.helper.HttpHelper import HttpHelper


class GitCloneOverHttp(GitClone):
    def __init__(self, number, args):
        super(GitCloneOverHttp, self).__init__(number, args, HttpHelper())
