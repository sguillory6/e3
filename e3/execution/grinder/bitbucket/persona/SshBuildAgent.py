from Instrumentation import instrument
from bitbucket.persona.base import BuildAgent
from bitbucket.scm import GitCloneOverSsh
from bitbucket.scm import GitLsRemoteSsh


class SshBuildAgent(BuildAgent):
    """
    A build agent that polls repositories for changes via SSH,
    it randomly clones "changed" repositories
    """
    def __init__(self, number, args):
        super(SshBuildAgent, self).__init__(number,
                                            args,
                                            GitCloneOverSsh,
                                            GitLsRemoteSsh)
        instrument()
