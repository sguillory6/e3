

class Branch(object):
    """
    Branch information
    """
    def __init__(self, identifier, display_identifier, latest_commit=None,
                 latest_change_set=None, is_default=False, branch_type="BRANCH"):
        self.latest_commit = latest_commit
        self.latest_change_set = latest_change_set
        self.branch_type = branch_type
        self.is_default = is_default
        self.identifier = identifier
        self.display_identifier = display_identifier

    def __repr__(self):
        return "Branch(identifier=%s, default=%s)" % (self.identifier, str(self.is_default))

    @classmethod
    def from_json(cls, j_branch):
        return cls(
            j_branch.get("id", None),
            j_branch.get("displayId", None),
            j_branch.get("latestCommit", None),
            j_branch.get("latestChangeset", None),
            j_branch.get("isDefault", None),
            j_branch.get("type", None),
        )
