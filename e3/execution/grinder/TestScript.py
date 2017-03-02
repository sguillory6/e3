import datetime
import os

from HTTPClient import NVPair
from java.lang import System
from java.net import ConnectException
from net.grinder.plugin.http import HTTPPluginControl
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.slf4j import LoggerFactory

from ProcessRunner import ProcessRunner
from Tools import *
from utils import encode_json, decode_json, load_script

connectionDefaults = HTTPPluginControl.getConnectionDefaults()
connectionDefaults.useContentEncoding = True
connectionDefaults.useTransferEncoding = True

httpUtilities = HTTPPluginControl.getHTTPUtilities()

connectionDefaults.defaultHeaders = [
    NVPair('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:47.0) Gecko/20100101 Firefox/47.0'),
    NVPair('Accept-Language', 'en-US,en;q=0.5')
]

ACCEPT_ALL = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8,en-AU;q=0.6',
}

ACCEPT_HTML = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8,en-AU;q=0.6'
}

ACCEPT_JSON = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8,en-AU;q=0.6',
    'X-Requested-With': 'XMLHttpRequest'
}

CONTENT_TYPE_FORM = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

CONTENT_TYPE_JSON = {
    'Content-Type': 'application/json'
}

ProcessRunner().call(["git", "config", "--global", "http.postBuffer", "524288000"])

# Global counter of Grinder tests.  Every TestScript has one "builtin" self.test (with the same number as the job
# number), and can optionally call create_test() to create additional tests, for example, for the many different
# interactions of a complex script.
global_test_count = 0


def create_request(test, url, headers=None):
    request = HTTPRequest(url=url)
    if headers:
        request.headers = headers
    test.record(request, HTTPRequest.getHttpMethodFilter())
    return request


# Create a new Grinder Test() object
def create_test(logger, description):
    global global_test_count
    number = global_test_count
    global_test_count += 1
    logger.info("Test %d: \"%s\"" % (number, description))
    return Test(number, description)


class TestScript(object):
    def __init__(self, number, args):
        # Ensure we don't write to the agent or worker logs
        self.logger = LoggerFactory.getLogger("atlassian")

        start_time = datetime.datetime.now()
        self.number = number
        self.args = args
        self.root = System.getProperty("root")
        self.test = Test(number, args["description"])
        self.test_data = self._create_test_data_provider(System.getProperty("testDataProvider"))
        self.info("Test %d: \"%s\"" % (number, args["description"]))
        grinder.getStatistics().delayReports = 1
        duration = datetime.datetime.now() - start_time
        self.debug("Took %s to init TestScript" % duration)

        # keep a link to the e3 temp folder
        self.e3_temp_dir = os.path.join(self.root, "tmp")

        # Request object for HTTP requests (if any) executed by test script subclasses
        self.request = HTTPRequest()
        self.test.record(self.request)

        # Process runner object for Git requests (if any) executed by test script subclasses
        self.runner = ProcessRunner()
        self.test.record(self.runner)

    def _create_test_data_provider(self, script_name):
        """
        Test data provider either by passed by environment variable -DtestDataProvider.
        When E3 run it will get that information from experiment file. So we could have difference test data provider
        for difference experiment/product
        :param script_name:
        :return:
        """
        self.logger.info("Creating test data provider %s" % script_name)
        test_data_provider_class = load_script(script_name)
        return test_data_provider_class()

    def rest(self, method, url, data=None):
        """
        Execute a REST action and optionally send and receive JSON
        :param method: GET, PUT, POST, DELETE
        :type method: str
        :param url: The URL of the rest endpoint
        :type url: str
        :param data: The data to send
        :type data: dict
        :return: The JSON response if applicable else None
        :rtype: dict
        """
        if url.startswith("http://") or url.startswith("https://"):
            real_url = url
        else:
            real_url = "%s%s" % (self.test_data.base_url, url)

        headers = self.to_grinder(ACCEPT_JSON) + self.to_grinder({
            "Origin": self.test_data.base_url
        })

        try:
            if method == "GET":
                res = self.request.GET(real_url, self.to_grinder(data), headers)
            elif method == "PUT" or method == "POST":
                body = encode_json(data)
                headers = headers + self.to_grinder(CONTENT_TYPE_JSON)
                if method == "PUT":
                    res = self.request.PUT(real_url, body, headers)
                else:
                    res = self.request.POST(real_url, body, headers)
            elif method == "DELETE":
                res = self.request.DELETE(real_url, headers)
            else:
                self.error("The requested method '%s' is not supported", method)
                raise ValueError("Requested HTTP method '%s' is not supported" % method)

            if is_http_ok() or is_redirect():
                if res.getStatusCode() == 204 or is_redirect():
                    return {}
                else:
                    return decode_json(res.getText())
            else:
                if not res:
                    res = get_last_response()
                self.error("REST: '%s' to '%s' failed. SC=[%d] PL=[%s]",
                           method, real_url, res.getStatusCode(), res.getText())
                return None
        except ConnectException:
            self.error("HTTP: '%s' to '%s' failed because the connection was refused", method, real_url)
            return None

    def http(self, method, url, data=None):
        """
        Execute a HTTP action
        :param method: GET, PUT, POST, DELETE
        :type method: str
        :param url: The URL of the rest endpoint
        :type url: str
        :param data: The data to send
        :type data: dict
        :return: The response as text
        :rtype: str
        """
        # Convert the url to absolute
        if url.startswith("http://") or url.startswith("https://"):
            real_url = url
        else:
            real_url = "%s%s" % (self.test_data.base_url, url)

        headers = self.to_grinder(ACCEPT_HTML)

        try:
            res = None
            if method == "GET":
                query_params = self.to_grinder(data)
                res = self.request.GET(real_url, query_params, headers)

            if method == "PUT" or method == "POST":
                body = self.to_grinder(data)
                headers += self.to_grinder(CONTENT_TYPE_FORM)
                if method == "PUT":
                    res = self.request.PUT(real_url, body, headers)
                else:
                    res = self.request.POST(real_url, body, headers)

            if method == "DELETE":
                res = self.request.DELETE(real_url, headers)

            redirect = is_redirect()
            if (is_http_ok() or redirect) and res:
                if redirect:
                    return ""
                return res.getText()
            else:
                if not res:
                    res = get_last_response()
                self.error("HTTP: '%s' to '%s' failed. SC=[%d] PL=[%s]", method, real_url,
                           res.getStatusCode(), res.getText())
                return None
        except ConnectException:
            self.error("HTTP: '%s' to '%s' failed because the connection was refused", method, real_url)
            return None

    def trace(self, message, *args):
        """
        Log a trace message
        :param message: The message to log, can contain format args
        :type message: str
        :param args:
        :type args: *args
        :return: Nothing
        """
        if self.logger.isTraceEnabled():
            self.logger.trace(message % args)

    def debug(self, message, *args):
        """
        Log a debug message
        :param message: The message to log, can contain format args
        :type message: str
        :param args:
        :type args: *args
        :return: Nothing
        """
        if self.logger.isDebugEnabled():
            self.logger.debug(message % args)

    def info(self, message, *args):
        """
        Log a info message
        :param message: The message to log, can contain format args
        :type message: str
        :param args:
        :type args: *args
        :return: Nothing
        """
        if self.logger.isInfoEnabled():
            self.logger.info(message % args)

    def warn(self, message, *args):
        """
        Log a warn message
        :param message: The message to log, can contain format args
        :type message: str
        :param args:
        :type args: *args
        :return: Nothing
        """
        if self.logger.isWarnEnabled():
            self.logger.warn(message % args)

    def error(self, message, *args):
        """
        Log a error message
        :param message: The message to log, can contain format args
        :type message: str
        :param args:
        :type args: *args
        :return: Nothing
        """
        if self.logger.isErrorEnabled():
            self.logger.error(message % args)

    @staticmethod
    def to_grinder(data):
        result = []
        if data:
            if isinstance(data, list):
                for h in data:
                    if not isinstance(h, dict):
                        raise TypeError("The data list did not contain a dict")
                    for k in h.keys():
                        result.append(NVPair(k, h[k]))
            elif isinstance(data, dict):
                for k in data.keys():
                    result.append(NVPair(k, data[k]))
            else:
                raise TypeError("The data is not a list or a dict")
        return result

    @staticmethod
    def get_thread_number():
        return grinder.getThreadNumber()

    @staticmethod
    def report_success(success):
        grinder.getStatistics().getForLastTest().success = success

    def run_git(self, args, runner=None, env=None, cwd=None):
        """
        Execute a git command as the current user

        :param args: The arguments to pass to git
        :type args: list(str)
        :param runner: The processes runner to use
        :type runner: ProcessRunner
        :param env: the environment to pass to git
        :type env: dict
        :param cwd: The working directory in which git will execute
        :type cwd: str
        :return: The git process return code
        :rtype: int
        """
        if runner:
            r = runner
        else:
            r = self.runner
        result = r.call(["git"] + args, env=env, cwd=cwd)
        self.report_success(result == 0)
        return result

    @staticmethod
    def sleep(millis):
        return grinder.sleep(millis)
