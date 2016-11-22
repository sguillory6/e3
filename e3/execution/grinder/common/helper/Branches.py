from TestScript import TestScript
from Tools import is_http_ok
from common.wrapper.Branch import Branch


def rest_get_default_branch(script, project_key, repo_slug):
    """
    Return the default branch for a given repository
    :param script:
    :param project_key:
    :param repo_slug:
    :return: the default branch
    :rtype: Branch
    """
    j = script.rest("GET", "/rest/api/1.0/projects/%s/repos/%s/branches/default" % (project, repository))
    if is_http_ok():
        return Branch.from_json(j)


def rest_get_branches(script, project, repository):
    """
    Gets a list of branches in a repository
    :param script: An instance of TestScript
    :type script: TestScript
    :param project: The project name
    :type project: str
    :param repository: The repository
    :type repository: str
    :return: a list of branches
    :rtype: list(str)
    """
    j = script.rest("GET", "/rest/api/1.0/projects/%s/repos/%s/branches" % (project, repository))
    if is_http_ok():
        return map(lambda branch: Branch.from_json(branch), j.get("values", []))


def rest_get_build_status(script, commit):
    """
    Get the build status of a commit hash
    :param script:
    :param commit:
    :return:
    """
    j = script.rest("GET", "/rest/build-status/latest/commits/stats/%s" % commit)
    if is_http_ok():
        return j


def get_branch_by_id(branches, branch_id):
    """
    Gets branch by ID from a list of branches retrieved from rest_get_branches()
    :param branches: A previously fetched list of branches
    :type branches: list(Branch)
    :param branch_id: The identifier of a branch to look up
    :type branch_id: str
    :return: The branch if found else None
    :rtype: Branch
    """
    possible_match = filter(lambda r: r.identifier == branch_id or r.display_identifier == branch_id, branches)
    return possible_match[0] if possible_match else None
