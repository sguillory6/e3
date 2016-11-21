

class Repository:
    """
    Repository information
    """
    def __init__(self, project_key, slug, project_id=None, repo_id=None):
        self.project_key = project_key
        self.slug = slug
        self.project_id = project_id
        self.repo_id = repo_id

    def __repr__(self):
        if self.project_id and self.repo_id:
            return "Repository(key = %s, slug = %s, project_id = %s, repo_id = %s" % \
                   (self.project_key, self.slug, self.project_id, self.repo_id)
        else:
            return "Repository(key = %s, slug = %s" % (self.project_key, self.slug)

    @classmethod
    def from_json(cls, repo_data):
        return cls(repo_data["project"]["key"],
                   repo_data["slug"],
                   repo_data["project"]["id"],
                   repo_data.get("id", None))
