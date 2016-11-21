import net.grinder.script.Grinder

import TestScript
from ProcessRunner import ProcessRunner


class TestProcessRunner(ProcessRunner):
    def __init__(self, description):
        ProcessRunner.__init__(self)
        self.logger.info("TestProcessRunner(self, \"" + description + "\")")
        self.test = TestScript.create_test(self.logger, description)
