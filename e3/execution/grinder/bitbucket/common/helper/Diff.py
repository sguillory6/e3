from bitbucket.common.helper.Branches import rest_get_build_status
from bitbucket.common.helper.Inbox import rest_get_inbox_count

from TestScript import TestScript
from Tools import is_http_ok


def view_diff(script, project_key, repo_slug, source_branch, target_branch, source_repo_id=0, target_repo_id=0):
    """
    Get the diff between two branches
    :param script: The TestScript instance
    :type script: TestScript
    :param project_key: The project key
    :param repo_slug: The repo slug
    :param source_branch: the source branch
    :type source_branch: Branch
    :param target_branch: the target branch
    :type target_branch: Branch
    :param source_repo_id: The source repository id (optional)
    :type source_repo_id: int
    :param target_repo_id: The target repository id (optional)
    :type target_repo_id: int
    :return:
    """
    diff_url = "/projects/%s/repos/%s/compare/diff" % (project_key, repo_slug)
    query_params = {
        "targetBranch": target_branch.identifier,
        "sourceBranch": source_branch.identifier
    }
    if target_repo_id > 0:
        query_params["targetRepoId"] = str(target_repo_id)

    script.http('GET', diff_url, query_params)
    if is_http_ok():
        # Load the rest resources
        rest_get_build_status(script, target_branch.latest_commit)
        rest_get_build_status(script, source_branch.latest_commit)

        changes = rest_get_changes(script, project_key, repo_slug, source_branch.latest_commit,
                                   target_branch.latest_commit, source_repo_id)

        rest_get_commits(script, project_key, repo_slug, source_branch.latest_commit, target_branch.latest_commit,
                         source_repo_id)

        rest_get_reviewers(script, project_key, repo_slug, source_branch.identifier, target_branch.identifier,
                           source_repo_id, target_repo_id)

        rest_get_inbox_count(script)

        filename_list = filter(lambda x: x['type'] == 'FILE', changes['values'])
        filename = filename_list[0]["path"]["toString"] if filename_list else None

        return rest_get_diff(script, filename, project_key,
                             repo_slug, source_branch.latest_commit, target_branch.latest_commit)


def rest_get_diff(script, filename, project_key, repo_slug, from_commit, to_commit,
                  with_markup=True, whitespace='', context_lines=-1, with_comments=False,
                  from_repo_id=0):
    diff_url = "/rest/api/latest/projects/%s/repos/%s/compare/diff/%s" % (project_key, repo_slug, filename)
    query_params = {
        "from": from_commit,
        "to": to_commit,
        "avatarSize": "64",
        "markup": "true" if with_markup else "false",
        "whitespace": whitespace,
        "contextLines": str(context_lines),
        "withComments": "true" if with_comments else "false",
        "autoSrcPath": "undefined"
    }
    if from_repo_id > 0:
        query_params['fromRepo'] = str(from_repo_id)

    return script.rest('GET', diff_url, query_params)


def rest_get_changes(script, project_key, repo_slug, from_commit, to_commit, from_repo_id=0):
    changes_url = "/rest/api/latest/projects/%s/repos/%s/compare/changes" % (project_key, repo_slug)
    query_params = {
        "start": "0",
        "limit": "1000",
        "from": from_commit,
        "to": to_commit
    }
    if from_repo_id > 0:
        query_params["fromRepo"] = str(from_repo_id)

    return script.rest('GET', changes_url, query_params)


def rest_get_commits(script, project_key, repo_slug, from_commit, to_commit, secondary_repository_id=0):
    commits_url = "/rest/api/latest/projects/%s/repos/%s/compare/commits" % (project_key, repo_slug)
    query_params = {
        "start": "0",
        "limit": "10",
        "from": from_commit,
        "to": to_commit
    }
    if secondary_repository_id > 0:
        query_params["secondaryRepositoryId"] = str(secondary_repository_id)

    return script.rest('GET', commits_url, query_params)


def rest_get_reviewers(script, project_key, repo_slug, source_branch, target_branch, source_repo_id=0, target_repo_id=0):
    reviewers_url = "/rest/default-reviewers/latest/projects/%s/repos/%s/reviewers" % (project_key, repo_slug)
    query_params = {
        "sourceRefId": source_branch,
        "targetRefId": target_branch
    }
    if source_repo_id > 0 and target_repo_id > 0:
        query_params["sourceRepoId"] = str(source_repo_id)
        query_params["targetRepoId"] = str(target_repo_id)

    return script.rest('GET', reviewers_url, query_params)
