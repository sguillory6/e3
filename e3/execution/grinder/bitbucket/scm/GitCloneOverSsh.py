from bitbucket.common.helper.SshHelper import SshHelper

from bitbucket.scm.base.GitClone import GitClone


class GitCloneOverSsh(GitClone):
    def __init__(self, number, args):
        super(GitCloneOverSsh, self).__init__(number, args, SshHelper())
