from scm.base.GitLsRemote import GitLsRemote
from common.helper.HttpHelper import HttpHelper


class GitLsRemoteHttp(GitLsRemote):
    def __init__(self, number, args):
        super(GitLsRemoteHttp, self).__init__(number, args, HttpHelper())
