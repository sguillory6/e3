from bitbucket.common.helper.SshHelper import SshHelper
from bitbucket.scm.base.GitLsRemote import GitLsRemote


class GitLsRemoteSsh(GitLsRemote):
    def __init__(self, number, args):
        super(GitLsRemoteSsh, self).__init__(number, args, SshHelper())
