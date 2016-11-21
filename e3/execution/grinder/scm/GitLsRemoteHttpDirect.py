from scm.base.GitLsRemote import GitLsRemote
from common.helper.HttpDirectHelper import HttpDirectHelper


class GitLsRemoteHttp(GitLsRemote):
    def __init__(self, number, args):
        super(GitLsRemoteHttp, self).__init__(number, args, HttpDirectHelper())
