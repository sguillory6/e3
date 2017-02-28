from bitbucket.common.helper.HttpHelper import HttpHelper
from bitbucket.scm.base.GitLsRemote import GitLsRemote


class GitLsRemoteHttp(GitLsRemote):
    def __init__(self, number, args):
        super(GitLsRemoteHttp, self).__init__(number, args, HttpHelper())
