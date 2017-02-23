from bitbucket.common.helper.SshHelper import SshHelper

from bitbucket.scm.base.PushChanges import PushChanges


class PushChangesSsh(PushChanges):
    def __init__(self, number, args):
        super(PushChangesSsh, self).__init__(number, args, SshHelper(), '%s/%s_%s')
