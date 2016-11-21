class Node:
    hostname = None
    username = None
    key_file = None

    def __init__(self, hostname, username, key_file):
        self.hostname = hostname
        self.username = username
        self.key_file = key_file

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<Server(%s@%s using key %s)>" % (self.username, self.hostname, self.key_file)
