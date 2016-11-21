from scm.base.GitClone import GitClone
from common.helper.HttpDirectHelper import HttpDirectHelper


class GitCloneOverHttpDirect(GitClone):
    def __init__(self, number, args):
        super(GitCloneOverHttpDirect, self).__init__(number, args, HttpDirectHelper())
