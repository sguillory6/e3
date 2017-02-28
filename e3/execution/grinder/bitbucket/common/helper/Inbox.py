from Tools import is_http_ok


def rest_get_inbox_count(script):
    """
    Gets the current pull request inbox count via REST
    :param script: An instance of TestScript
    :type script: TestScript
    :return: The number of items in the inbox
    :rtype: int
    """
    j = script.rest("GET", '/rest/api/latest/inbox/pull-requests/count')
    if is_http_ok():
        return int(j.get('count', 0))
    return 0
