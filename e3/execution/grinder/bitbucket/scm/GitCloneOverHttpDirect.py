from bitbucket.common.helper.HttpDirectHelper import HttpDirectHelper
from bitbucket.scm.base.GitClone import GitClone


class GitCloneOverHttpDirect(GitClone):
    def __init__(self, number, args):
        super(GitCloneOverHttpDirect, self).__init__(number, args, HttpDirectHelper())
