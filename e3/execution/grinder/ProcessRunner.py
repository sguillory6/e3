import subprocess

from org.slf4j import LoggerFactory


def quote_if_necessary(s):
    s = s.replace("\"", "\\\"")
    if s.find(" ") == -1:
        return s
    else:
        return "\"" + s + "\""


class ProcessRunner:
    def __init__(self):
        # Ensure we don't write to the agent or worker logs
        self.logger = LoggerFactory.getLogger("atlassian")

    def call(self, args, cwd=None, env=None):
        pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=env)
        (stdout, stderr) = pipe.communicate()
        result = pipe.returncode
        if result != 0:
            command_line = "%s" % " ".join(map(quote_if_necessary, args))
            self.logger.warn("%s -> exit code %d" % (command_line, result))
            if len(stdout) > 0:
                self.logger.info("Standard output: %s" % stdout)
            if len(stderr) > 0:
                self.logger.info("Standard error: %s" % stderr)

        return result
