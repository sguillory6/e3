from scm.base.GitClone import GitClone
from common.helper.SshHelper import SshHelper


class GitCloneOverSsh(GitClone):
    def __init__(self, number, args):
        super(GitCloneOverSsh, self).__init__(number, args, SshHelper())
