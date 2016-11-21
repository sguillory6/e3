from scm.base.GitLsRemote import GitLsRemote
from common.helper.SshHelper import SshHelper


class GitLsRemoteSsh(GitLsRemote):
    def __init__(self, number, args):
        super(GitLsRemoteSsh, self).__init__(number, args, SshHelper())
