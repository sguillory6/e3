from Instrumentation import instrument
from persona.base.BuildAgent import BuildAgent
from scm.GitCloneOverSsh import GitCloneOverSsh
from scm.GitLsRemoteSsh import GitLsRemoteSsh


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
