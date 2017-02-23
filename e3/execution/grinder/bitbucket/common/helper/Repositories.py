import random
import re

from TestScript import TestScript
from Tools import is_http_ok, get_form_variable, is_http_code, get_redirect
from bitbucket.common.wrapper import Repository

REPOS_LIST_RE = re.compile("data-repository-id=\"[0-9]*\">([^<]*)")
REPO_ERRORS_RE = re.compile("<div class=\"error\">([^<]*)")


def choose_repository_at_random(script, project=None):
    """
    Gets a list of repositories and picks one at random
    :param script: A TestScript instance
    :type script: TestScript
    :param project: Limit the repos to the project (optional)
    :type project: str
    :return: the randomly chosen repository
    :rtype: Repository
    """
    repositories = rest_get_repositories(script, project, limit=1000)
    if is_http_ok() and isinstance(repositories, list) and len(repositories) > 0:
        return random.choice(repositories)


def create_repository(script, project, repository):
    """
    Gets the list of repositories for the specified project
    :param script: A TestScript instance
    :type script: TestScript
    :param project: The project for the repository
    :type project: str
    :param repository: The repository to browse
    :type repository: str
    :return: True if created else False
    :rtype: bool
    """
    script.http("GET", "/projects/%s/repos?create" % project)
    if is_http_ok():
        token = get_form_variable("atl_token", True)
        if not token:
            script.error("Failed to find XSRF token")
        else:
            body = script.http("POST", "/projects/%s/repos?create" % project, {
                'name': repository,
                'scmId': 'git',
                'forkable': 'true',
                'submit': 'Create repository',
                'atl_token': token
            })
            if is_http_ok():
                # Normally returns 200 if there is an error, so we get them and report a failue
                errors = REPO_ERRORS_RE.finditer(body)
                error_list = map(lambda err: err.group(1), errors)
                if len(error_list) > 0:
                    script.warn("Failed to create repository due to the following errors: %s", error_list)
            elif is_http_code(302):
                # When a 302 (found) is returned the repository was created, and we are directed to it
                script.http("GET", get_redirect())
                if is_http_ok():
                    return True
    return False


def browse_repository(script, project, repository):
    """
    Gets the list of repositories for the specified project
    :param script: A TestScript instance
    :type script: TestScript
    :param project: The project for the repository
    :type project: str
    :param repository: The repository to browse
    :type repository: str
    :return: The browse response as a string
    :rtype: str
    """
    return script.http("GET", "/projects/%s/repos/%s/browse" % (project, repository))


def delete_repository(script, project, repository):
    """
    Deletes the specified repository from the specified project
    :param script: A TestScript instance
    :type script: TestScript
    :param project: The project for the repository
    :type project: str
    :param repository: The repository to delete
    :type repository: str
    :return: True if deleted else False
    :rtype: bool
    """
    script.http("GET", "/projects/%s/repos/%s/settings" % (project, repository))
    if is_http_ok():
        script.rest("DELETE", "/projects/%s/repos/%s" % (project, repository))
        if is_http_code(202):
            return True
    return False


def get_repositories(script, project):
    """
    Gets the list of repositories for the specified project
    :param script: A TestScript instance
    :type script: TestScript
    :param project: The project for the repositories to list
    :type project: str
    :return: repositories or empty list
    :rtype: list(Repository)
    """
    body = script.http("GET", "/projects/%s" % project)
    if is_http_ok():
        return map(lambda m: Repository(project, m.group(1)), REPOS_LIST_RE.finditer(body))


def rest_get_repository(script, project_key, repo_slug):
    """
    Get a repository via REST
    :param script: A TestScript instance
    :type script: TestScript
    :param project_key: An optional project
    :type project_key: str
    :param repo_slug:
    :type repo_slug: str
    :return: A repository
    :rtype: Repository
    """
    repo_url = "/rest/api/latest/projects/%s/repos/%s" % (project_key, repo_slug)
    j = script.rest("GET", repo_url)
    return Repository.from_json(j)


def rest_get_repositories(script, project=None, start=0, limit=50):
    """
    Gets a list of repositories via REST
    :param script: A TestScript instance
    :type script: TestScript
    :param project: An optional project
    :type project: str
    :param start: The offset to start from
    :type start: int
    :param limit: The max number of items to return
    :type limit: int
    :return: repositories or None
    :rtype: list(Repository)
    """
    if project:
        project_filter = "projects/%s/" % project
    else:
        project_filter = ""

    j = script.rest("GET", "/rest/api/latest/%srepos" % project_filter, {
        "start": str(start),
        "limit": str(limit)
    })

    if is_http_ok():
        return map(lambda repo: Repository(repo["project"]["key"], repo["slug"]), j["values"])


def rest_get_recent_repositories(script, limit=0):
    """
    Get the recently access repositories via REST
    :param script: An instance of TestScript
    :type script: TestScript
    :param limit: limit the results
    :type limit: int
    :return: a list of slugs
    :rtype: list(Repository)
    """
    data = {"limit": limit} if limit > 0 else None
    j = script.rest("GET", '/rest/api/latest/profile/recent/repos', data)
    slugs = []
    if is_http_ok():
        for repo in j.get("values", []):
            project_key = repo.get('project', {'key': None}).get('key')
            repo_slug = repo.get('slug', None)
            slugs.append(Repository(project_key, repo_slug))
    return slugs


def rest_get_repo_pr_settings(script, project_key, repo_slug):
    """
    Gets the settings for PRs for the specified repo
    :param script: a TestScript instance
    :type script: TestScript
    :param project_key: The project key
    :type project_key: str
    :param repo_slug: The repo slug
    :type repo_slug: str
    :return: the repo pr settings
    :rtype: dict
    """
    repo_pr_settings_url = "/rest/api/latest/projects/%s/repos/%s/settings/pull-requests" % (project_key, repo_slug)
    return script.rest("GET", repo_pr_settings_url)
