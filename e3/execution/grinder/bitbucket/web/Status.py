from TestScript import TestScript
from utils import decode_json


class Status(TestScript):
    def __init__(self, number, args):
        super(Status, self).__init__(number, args)

    def __call__(self):
        response = self.request.GET("%s/status" % self.test_data.base_url)
        json = decode_json(response.text)
        self.report_success("state" in json and json["state"] == "RUNNING")
        self.sleep(500)
