

class Project:
    """
    Project information
    """
    def __init__(self, project_key, project_id=None):
        self.project_key = project_key
        self.project_id = project_id

    def __repr__(self):
        if self.project_id:
            return "Project(key = %s, id = %s)" % (self.project_key, self.project_id)
        else:
            return "Project(key = %s)" % self.project_key

    @classmethod
    def from_json(cls, repo_data):
        return cls(repo_data["key"],
                   repo_data.get("id", None))
