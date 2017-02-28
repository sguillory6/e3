from bitbucket.scm.GitLsRemoteHttp import GitLsRemoteHttp
from bitbucket.scm.GitCloneOverHttp import GitCloneOverHttp
from bitbucket.persona.base.BuildAgent import BuildAgent

from Instrumentation import instrument


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
