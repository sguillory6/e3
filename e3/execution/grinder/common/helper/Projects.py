import random
import re

from TestScript import TestScript
from Tools import is_http_ok, get_form_variable, is_http_code, get_redirect
from common.wrapper.Project import Project

PROJECT_LIST_RE = re.compile("<td class=\"project-key\">([^<]*)")
PROJECT_ERRORS_RE = re.compile("<div class=\"error\">([^<]*)")


def choose_project_at_random(script):
    """
    Gets a list of projects and picks one at random
    :param script: A TestScript instance
    :type script: TestScript
    :return: the randomly chosen project
    :rtype: str
    """
    projects = rest_get_projects(script, limit=1000)
    if projects and isinstance(projects, list) and len(projects) > 0:
        return random.choice(projects)


def create_project(script, name, description):
    """
    Creates a a project
    :param script: An instance of TestScript
    :type script: TestScript
    :param name: The name of the project
    :type name: str
    :param description: The description of the project
    :type description: str
    :return: True for success, False for failure
    :rtype: bool
    """
    script.http("GET", "/projects?create")
    if is_http_ok():
        token = get_form_variable("atl_token", True)
        if not token:
            script.warn("No XSRF token found")
        else:
            body = script.http("POST", "/projects?create", {
                "name": name,
                "key": name.upper(),
                "description": description,
                "avatar": '',
                "submit": "Create project",
                "atl_token": token
            })
            if is_http_ok():
                # Normally returns 200 if there is an error, so we get them and report a failue
                errors = PROJECT_ERRORS_RE.finditer(body)
                error_list = map(lambda err: err.group(1), errors)
                if len(error_list) > 0:
                    script.warn("Failed to create project due to the following errors: %s", error_list)
            elif is_http_code(302):
                # When a 302 (found) is returned the project was created, and we are directed to it
                script.http("GET", get_redirect())
                if is_http_ok():
                    return True
    return False


def delete_project(script, name):
    """
    Deletes a project
    :param script: An instance of TestScript
    :type script: TestScript
    :param name: The name of the project
    :type name: str
    :return: True for success, False for failure
    :rtype: bool
    """
    script.http("GET", "/projects/%s/settings" % name)
    if is_http_ok():
        script.rest("DELETE", "/projects/%s" % name)
        if is_http_ok():
            return True
    return False


def get_projects(script):
    """
    Gets the list of projects
    :param script: A TestScript instance
    :type script: TestScript
    :return: projects or empty list
    :rtype: list(str)
    """
    body = script.http("GET", "/projects", {"limit": "20"})
    matches = PROJECT_LIST_RE.finditer(body)
    return map(lambda m: m.group(1), matches)


def rest_get_projects(script, start=0, limit=50):
    """
    Gets a list of projects via REST
    :param script: A TestScript instance
    :type script: TestScript
    :param start: The offset to start from
    :type start: int
    :param limit: The max number of items to return
    :type limit: int
    :return: projects or empty list
    :rtype: list(str)
    """
    j = script.rest("GET", "/rest/api/latest/projects", {"start": str(start), "limit": str(limit)})
    if is_http_ok():
        return map(lambda project: project["key"],  j["values"])


def rest_get_project(script, project_key):
    """
    Get a project via REST
    :param script: A TestScript instance
    :type script: TestScript
    :param project_key: An optional project
    :type project_key: str
    :return: A repository
    :rtype: Project
    """
    repo_url = "/rest/api/latest/projects/%s" % project_key
    j = script.rest("GET", repo_url)
    return Project.from_json(j)
