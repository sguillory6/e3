import random

from TestScript import TestScript
from Tools import get_form_variable, is_redirect, is_http_ok, get_redirect, get_last_response
from common.helper.Repositories import rest_get_repo_pr_settings


def create_pull_request(script, project_key, repo_slug, source_branch, target_branch, title=None, description=None,
                        reviewers=list(), source_repo_id=0, target_repo_id=0):
    """
    Create a pull request
    :param script: A TestScript instance
    :type script: TestScript
    :param project_key: The project key
    :type project_key: str
    :param repo_slug: The repo slug
    :type repo_slug: str
    :param source_branch: The source branch (aka feature branch)
    :type source_branch: str
    :param target_branch: The target branch (normally master)
    :type target_branch: str
    :param title: The PR title
    :type title: str
    :param description: The PR description
    :type description: str
    :param reviewers: The reviewers
    :type reviewers: list(User)
    :param source_repo_id: The id of the source repository
    :type source_repo_id: int
    :param target_repo_id: The id of the target repository
    :type target_repo_id: int
    :return: The pull request id or None if it can not be created
    :rtype: str
    """
    # First we load the create PR web page
    pr_form_url = "/projects/%s/repos/%s/pull-requests" % (project_key, repo_slug)
    query_params = {
        "create": "",
        "sourceBranch": source_branch,
        "targetBranch": target_branch
    }
    if target_repo_id > 0:
        query_params["targetRepoId"] = str(target_repo_id)

    script.http("GET", pr_form_url, query_params)

    if not is_http_ok():
        script.warn("Unable to load pull request create page")
    else:
        token = get_form_variable("atl_token", True)

        form_variables = {
            "fromBranch": source_branch,
            "toBranch": target_branch,
            "title": title,
            "description": description,
            "reviewers": "|!|".join(reviewers),
            "atl_token": token
        }
        if source_repo_id > 0:
            form_variables["fromRepoId"] = str(source_repo_id)
        if target_repo_id > 0:
            form_variables["toRepoId"] = str(target_repo_id)

        result = script.http("POST", pr_form_url + "?create", form_variables)

        if is_http_ok():
            if 'is already up-to-date with branch' in result:
                # No changes on branch!
                script.warn("The branch is already up to date with master!")
                return None

        if not is_redirect():
            script.warn("Unable to create pull request: HTTP %d Body %s", get_last_response().statusCode, result)
        else:
            # PR creation does a redirect to the PR
            redirect_url = get_redirect()
            _, pr_id = redirect_url.rsplit("/", 1)
            script.http("GET", redirect_url)
            if not is_redirect():
                script.warn("Unable to create pull request: HTTP %d Body %s", get_last_response().statusCode, result)
            else:
                # The PR page redirects to overview
                script.http("GET", get_redirect())

                rest_get_pr_merge(script, project_key, repo_slug, pr_id)
                rest_get_pr_jira_issues(script, project_key, repo_slug, pr_id)
                rest_get_repo_pr_settings(script, project_key, repo_slug)

                return pr_id


def merge_pr(script, project_key, repo_slug, source_branch, pr_id, pr_version=0, merge_message=''):
    """
    Merge a PR
    :param script: a TestScript instance
    :type script: TestScript
    :param project_key: The project key
    :type project_key: str
    :param repo_slug: The repo slug
    :type repo_slug: str
    :param source_branch: The target branch
    :type source_branch: str
    :param pr_id: The PR id of the PR to merge
    :type pr_id: str
    :param pr_version: The version of the PR
    :type pr_version: int
    :param merge_message: The optional merge message
    :type merge_message: str
    :return: True if the PR was merged else False
    :rtype: bool
    """
    auto_merge_url = "/rest/branch-utils/latest/projects/%s/repos/%s/automerge/path" % (project_key, repo_slug)
    script.rest("GET", auto_merge_url, {
        "branchRefId": source_branch
    })

    src_delete_url = "/rest/pull-request-source-branch-deletion/1.0/projects/%s/repos/%s/" \
                     "pull-requests/%s?dryRun=%%s" % (project_key, repo_slug, pr_id)
    script.rest("POST", src_delete_url % "true")

    if not is_http_ok():
        script.warn("Unable to delete source branch (dry run): %s", source_branch)

    merge_url = "/rest/api/latest/projects/%s/repos/%s/pull-requests/%s/merge?avatarSize=16&version=%s" % \
                (project_key, repo_slug, pr_id, str(pr_version))
    script.rest("POST", merge_url, {
        "message": merge_message
    })

    script.rest("POST", src_delete_url % "false")

    if not is_http_ok():
        script.warn("Unable to delete source branch (real deal): %s", source_branch)
        return False

    return True


def decline_pr(script, project_key, repo_slug, pr_id, pr_version=0):
    """
    Decline a PR
    :param script: a TestScript instance
    :type script: TestScript
    :param project_key: The project key
    :type project_key: str
    :param repo_slug: The repo slug
    :type repo_slug: str
    :param pr_id: The PR id of the PR to merge
    :type pr_id: str
    :param pr_version: The version of the PR
    :type pr_version: int
    :return: True of the PR was merged else False
    :rtype: bool
    """
    decline_url = "/rest/api/latest/projects/%s/repos/%s/pull-requests/%s/decline?avatarSize=16&version=%s" % \
                  (project_key, repo_slug, pr_id, str(pr_version))

    script.rest("POST", decline_url)

    if not is_http_ok():
        script.warn("Unable to decline PR [%s] in [%s/%s]", pr_id, project_key, repo_slug)
        return False

    return True


def get_pr_list(script, project_key, repo_slug, state="OPEN", target_branch=None):
    """
    Gets the list of PRs
    :param script: a TestScript instance
    :type script: TestScript
    :param project_key: The project key
    :type project_key: str
    :param repo_slug: The repo slug
    :type repo_slug: str
    :param state: The state filter ("OPEN", "MERGED", "DECLINED", "ALL")
    :type state: str
    :param target_branch: The target branch
    :type target_branch: str
    :return: The page payload
    :rtype: str
    """
    pr_list_url = "/projects/%s/repos/%s/pull-requests" % (project_key, repo_slug)
    query_params = {
        "avatarSize": "64",
        "order": "newest",
        "start": "0",
        "state": state
    }
    if target_branch:
        query_params["at"] = target_branch
    # "role.1": "AUTHOR/REVIEWER",
    # "username.1": "admin",
    return script.http("GET", pr_list_url, query_params)


def rest_get_pr_by_id(script, project_key, repo_slug, pr_id):
    pr_url = "/rest/api/latest/projects/%s/repos/%s/pull-requests/%s" % (project_key, repo_slug, pr_id)
    return script.rest("GET", pr_url)


def rest_get_pr_list(script, project=None, repo=None, start=0, limit=50):
    """
    Gets a list of pull requests via REST
    :param script: A TestScript instance
    :type script: TestScript
    :param project: The project key
    :type project: str
    :param repo: The repo slug
    :type repo: str
    :param start: The offset to start from
    :type start: int
    :param limit: The max number of items to return
    :type limit: int
    :return: pull request IDs or empty list
    :rtype: list(str)
    """
    j = script.rest("GET", "/rest/api/latest/projects/%s/repos/%s/pull-requests" % (project, repo),
                    {"start": str(start), "limit": str(limit)})
    if is_http_ok():
        return map(lambda pull_requests: pull_requests["id"],  j["values"])


def rest_get_pr_merge(script, project_key, repo_slug, pr_id):
    """
    Gets the merge status of the PR via REST
    :param script: a TestScript instance
    :type script: TestScript
    :param project_key: The project key
    :type project_key: str
    :param repo_slug: The repo slug
    :type repo_slug: str
    :param pr_id: the pull request id
    :type pr_id: Union(int, str)
    :return: the pr merge state
    :rtype: dict
    """
    pr_merge_url = "/rest/api/latest/projects/%s/repos/%s/pull-requests/%s/merge" % \
                   (project_key, repo_slug, str(pr_id))
    return script.rest("GET", pr_merge_url)


def rest_get_pr_jira_issues(script, project_key, repo_slug, pr_id):
    """
    Gets the merge status of the PR via REST
    :param script: a TestScript instance
    :type script: TestScript
    :param project_key: The project key
    :type project_key: str
    :param repo_slug: The repo slug
    :type repo_slug: str
    :param pr_id: the pull request id
    :type pr_id: Union(int, str)
    :return: the pr merge state
    :rtype: dict
    """
    pr_issues_url = "/rest/jira/latest/projects/%s/repos/%s/pull-requests/%s/issues" % \
                    (project_key, repo_slug, str(pr_id))
    return script.rest("GET", pr_issues_url)


def rest_get_pr_changes(script, project_key, repo_slug, pr_id, change_scope="unreviewed"):
    """
    Get the code changes for the PR
    :param script: a TestScript instance
    :type script: TestScript
    :param project_key: the project key
    :type project_key: str
    :param repo_slug: the repo slug
    :type repo_slug: str
    :param pr_id: the pull request id
    :type pr_id: str
    :param change_scope: the change scope (default is unreviewed)
    :type change_scope: str
    :return: The changes
    :rtype: dict
    """
    changes_url = "/rest/api/latest/projects/%s/repos/%s/pull-requests/%s/changes" % (project_key, repo_slug, pr_id)
    query_params = {
        "start": "0",
        "limit": "1000",
        "changeScope": change_scope
    }
    return script.rest("GET", changes_url, query_params)


def rest_get_pr_diff(script, project_key, repo_slug, pr_id, filename,
                     with_markup=True, whitespace='', context_lines=-1, with_comments=True):
    """
    Gets a diff for a particular file in a PR
    :param script: a TestScript instance
    :type script: TestScript
    :param project_key: the project key
    :type project_key: str
    :param repo_slug: the repo slug
    :type repo_slug: str
    :param pr_id: the pull request id
    :type pr_id: str
    :param filename: The file to diff
    :type filename: str
    :param with_comments: include comments
    :type with_comments: bool
    :param context_lines: no of context liens
    :type context_lines: int
    :param whitespace: show whitespace
    :type whitespace: str
    :param with_markup: include markup
    :type with_markup: bool
    :return: The diff
    :rtype: dict
    """
    pr_diff_url = "/rest/api/latest/projects/%s/repos/%s/pull-requests/%s/diff/%s" % \
                  (project_key, repo_slug, pr_id, filename)
    query_params = {
        "avatarSize": "64",
        "markup": "true" if with_markup else "false",
        "whitespace": whitespace,
        "contextLines": str(context_lines),
        "withComments": "true" if with_comments else "false",
        "autoSrcPath": "undefined"
    }
    return script.rest("GET", pr_diff_url, query_params)


def choose_pull_request_at_random(script, project=None, repo=None):
    """
    Gets a list of pull requests and picks one at random
    :param script: A TestScript instance
    :type script: TestScript
    :param project: Limit the pull requests to the project (optional)
    :type project: str
    :param repo: Limit the pull requests to the repo (optional)
    :type repo: str
    :return: the randomly chosen pull request ID
    :rtype: str
    """
    pull_requests = rest_get_pr_list(script, project, repo, limit=1000)
    if pull_requests and isinstance(pull_requests, list):
        return random.choice(pull_requests)
