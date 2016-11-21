from common.helper.HttpHelper import HttpHelper
from scm.base.PushChanges import PushChanges


class PushChangesHttp(PushChanges):
    def __init__(self, number, args):
        super(PushChangesHttp, self).__init__(number, args, HttpHelper())
