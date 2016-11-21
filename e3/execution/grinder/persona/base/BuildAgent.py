import datetime

from TestScript import TestScript


class BuildAgent(TestScript):
    """
    Base class for build agents that poll and clone repositories
    """
    def __init__(self, number, args, cloner, poller):
        super(BuildAgent, self).__init__(number, args)
        self.clone = cloner(self.number, self.args)
        self.poll = poller(self.number, self.args)

    def __call__(self):
        now_sec = datetime.datetime.now().second
        time_to_poll = (5 - (now_sec % 5))
        time_to_clone = (30 - (now_sec % 30))

        if time_to_clone <= time_to_poll:
            self.sleep(time_to_clone * 1000)
            self.clone()
        else:
            self.sleep(time_to_poll * 1000)
            self.poll()
