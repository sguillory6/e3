from TestScript import TestScript
from Tools import is_http_ok, get_redirect, is_redirect
from bitbucket.common.wrapper.User import User


def login(script, user):
    """
    Log in as the specified user
    :param script: An instance of TestScript
    :type script: TestScript
    :param user: The user dict containing 'username' and 'password'
    :type user: User | dict
    :return: True if successful else False
    :rtype: bool
    """
    if isinstance(user, User):
        username = user.username
        password = user.password
    else:
        username = user['username']
        password = user['password']
    login_form_data = {
        "j_username": username,
        "j_password": password
    }
    script.http("GET", "/login")
    if is_http_ok():
        script.http("POST", "/j_atl_security_check", login_form_data)
        # Login always redirects
        # But if it redirects to itself the login failed
        if "/login" not in get_redirect():
            return True
    script.warn("Logging in as user '%s' failed", user)
    return False


def logout(script):
    """
    Log out the currently logged in user
    :param script: An instance of the TestScript
    :type script: TestScript
    :return: Nothing
    :rtype: None
    """
    script.http("GET", "/j_atl_security_logout")
    if is_http_ok():
        if is_redirect():
            script.http("GET", get_redirect())
