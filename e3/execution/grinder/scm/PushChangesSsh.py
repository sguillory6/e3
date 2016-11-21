from scm.base.PushChanges import PushChanges
from common.helper.SshHelper import SshHelper


class PushChangesSsh(PushChanges):
    def __init__(self, number, args):
        super(PushChangesSsh, self).__init__(number, args, SshHelper(), '%s/%s_%s')
