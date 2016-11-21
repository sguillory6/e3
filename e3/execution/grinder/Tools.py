import uuid
from urlparse import urlparse

from net.grinder.plugin.http import HTTPPluginControl
from net.grinder.script import Test

httpUtilities = HTTPPluginControl.getHTTPUtilities()


def get_form_variable(element_name, hidden=False, after_text=None):
    """
    Gets the value of a form element
    :param element_name: The name of the form element
    :type element_name: str
    :param hidden: Is a hidden form element
    :type hidden: bool
    :param after_text: Only search from after this literal
    :type after_text: str
    :return: The value of the form element or ""
    :rtype: str
    """
    if hidden:
        if after_text:
            return httpUtilities.valueFromHiddenInput(element_name, after_text)
        else:
            return httpUtilities.valueFromHiddenInput(element_name)
    else:
        if after_text:
            return httpUtilities.valueFromBodyInput(element_name, after_text)
        else:
            return httpUtilities.valueFromBodyInput(element_name)


def get_http_clone_url(base_url, user, project_key, repo_slug):
    """
    Construct a clone URL to clone over http or https
    :param base_url: The base url
    :type base_url: str
    :param user: The user (used for authentication information)
    :type user: User
    :param project_key: The project key
    :type project_key: str
    :param repo_slug: The repository slug
    :type repo_slug: str
    :return: A HTTP URL that can be used to clone from
    :rtype: str
    """
    url_parse_res = urlparse(base_url)
    if url_parse_res.port:
        port = ":%d" % url_parse_res.port
    else:
        port = ""
    repo_git_url = "%s://%s:%s@%s%s/scm/%s/%s.git" % (
        url_parse_res.scheme,
        user.username,
        user.password,
        url_parse_res.hostname,
        port,
        project_key,
        repo_slug)
    return repo_git_url


def get_last_response():
    """
    Gets the last response
    :return: The last response
    :rtype: HTTPResponse
    """
    return httpUtilities.getLastResponse()


def get_redirect():
    """
    Get the "Location" header and expand to absolute URI
    :return: the redirect location
    :rtype: str
    """
    redirect = ""
    response = httpUtilities.getLastResponse()
    if response and response.getStatusCode() == 302:
        loc = str(response.getHeader("Location"))
        if loc:
            redirect = loc
    return redirect


def is_http_code(status_code):
    """
    Checks if the response has returned the desired status code
    :param status_code: The desired sc
    :rtype status_code: int
    :return: True if OK else False
    :rtype: bool
    """
    response = get_last_response()
    if response:
        return response.getStatusCode() == status_code
    return False


def is_http_ok():
    """
    Checks if the response is OK
    :return: True if OK else False
    :rtype: bool
    """
    response = get_last_response()
    if response:
        return 200 <= response.getStatusCode() < 300
    return False


def is_redirect():
    """
    Checks if the last response was a Redirect
    :return: True if redirect else False
    :rtype: bool
    """
    return get_last_response().getStatusCode() == 302


def register(identifier, name, method):
    """
    Register a method for instrumentation
    :param identifier: A number to uniquely identify the registered method
    :type identifier: int
    :param name: The short name of the operation
    :param method: The method to register
    :type method: function
    :return: Nothing
    """
    t = Test(identifier, name)
    t.record(method)


def random_uuid():
    return uuid.uuid4()

__all__ = [
    "get_form_variable", "get_last_response", "get_redirect",
    "is_http_ok", "is_redirect",
    "register"
]
