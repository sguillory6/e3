from Instrumentation import instrument
from persona.base.BuildAgent import BuildAgent
from scm.GitCloneOverHttp import GitCloneOverHttp
from scm.GitLsRemoteHttp import GitLsRemoteHttp


class HttpBuildAgent(BuildAgent):
    """
    A build agent that polls repositories for changes via HTTP,
    it randomly clones "changed" repositories
    """
    def __init__(self, number, args):
        super(HttpBuildAgent, self).__init__(number,
                                             args,
                                             GitCloneOverHttp,
                                             GitLsRemoteHttp)
        instrument()
