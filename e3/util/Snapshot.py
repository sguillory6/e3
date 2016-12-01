#!/usr/bin/env python

import datetime
import json
import math
import os
import random
from json import encoder

import click
import requests


class Snapshot:
    """
    Connects to a Bitbucket Server instance and generates a json file representing the data on the instance
    """

    def __init__(self, url, key_file, username, password, max_project, max_repo, max_branch, max_user, distribution,
                 distribution_factor, description, name, aws):
        self.url = url
        self.key_file = key_file
        self.username = username
        self.password = password
        self.max_project = int(max_project)
        self.max_repo = int(max_repo)
        self.max_branch = int(max_branch)
        self.max_user = int(max_user)
        self.distribution = distribution
        self.distribution_factor = float(distribution_factor)
        self.description = description
        self.name = name
        self.credentials = (username, password)
        self.e3_home = os.path.join(os.path.realpath(os.path.dirname(__file__)), "..", "..", "e3-home")
        self.output_file = os.path.join(self.e3_home, "snapshots", name + ".json")
        self.aws = aws
        # Seed the random number generator so that subsequent runs will apply an identical weight to snapshots.
        # 42 is chosen because it is the answer to the ultimate question of life, the universe, and everything.
        random.seed(42)
        # The number of repos that where actually generated by the script
        self.generated_repo_count = 0
        # A data structure representing project/repositories that will be written to the snapshot
        self.projects = []

    def generate(self):
        start_time = datetime.datetime.now().replace(microsecond=0)
        self.generate_snapshot()
        self.weight_snapshot()
        users = self.generate_users()
        snapshot = {"name": self.name,
                    "description": self.description,
                    "projects": self.projects,
                    "users": users}
        if self.aws == "true":
            aws_scaffold = {
                "ebs": {
                    "ap-southeast-2": "TODO"
                },
                "rds": {
                    "account": "TODO",
                    "id": "TODO"
                },
                "es": {
                    "snapshot": "TODO",
                    "bucket": "TODO"
                }
            }
            snapshot.update(aws_scaffold)
        with open(self.output_file, 'w') as jsonFile:
            json.dump(snapshot, jsonFile, indent=4, sort_keys=True)

        print "Snapshot %s written to %s with %d repositories, %d users, a weighting distribution of %s and" \
              " a distribution factor of %d it took %s" % (
                  self.name, self.output_file, self.generated_repo_count, len(users), self.distribution,
                  self.distribution_factor, datetime.datetime.now().replace(microsecond=0) - start_time)

    def generate_users(self):
        print "Generating maximum of %s users" % self.max_user
        keymap = open(os.path.join(self.e3_home, "keys", self.key_file + ".json"))
        keys = json.loads(keymap.read())

        prefilter_usernames = [username['name'] for username in
                               requests.get('%s/rest/api/1.0/users?limit=%s' % (self.url, self.max_user),
                                            auth=self.credentials).json()['values']]
        usernames = filter(lambda x: not x.startswith("admin"), prefilter_usernames)

        users = []
        for username in usernames:
            public_key = self.user_public_key(username)
            pks = public_key.split(" ")

            # Only add user if they have a SSH key
            if len(pks) > 1:
                user = {'username': username}
                lookup = pks[0] + " " + pks[1]
                for key in keys['key_pairs']:
                    if key['public_key'] == lookup:
                        user['public_key'] = public_key
                        user['private_key'] = key['private_key']
                        # LDAP dataset user passwords default to "password"
                        user['password'] = 'password'
                        users.append(user)

        return users

    def user_public_key(self, user):
        public_key = [key['text'] for key in requests.get('%s/rest/ssh/1.0/keys?user=%s' % (self.url, user),
                                                          auth=self.credentials).json()['values']]
        if len(public_key) > 0:
            return public_key[0]
        else:
            return ""

    def generate_snapshot(self):
        print("Generating snapshot with %s max projects, max %s repositories in each, max %s branches per repo."
              % (self.max_project, self.max_repo, self.max_branch))
        projects = [project['key'] for project in requests.get('%s/rest/api/1.0/projects?limit=%s'
                                                               % (self.url, self.max_project),
                                                               auth=self.credentials).json()['values']]
        if len(projects) < 1:
            raise Exception("Could not find any projects on instance.")

        for i, project in enumerate(projects):
            repos = [repo['slug'] for repo in
                     requests.get('%s/rest/api/1.0/projects/%s/repos?limit=%s' % (self.url, project, self.max_repo),
                                  auth=self.credentials).json()['values']]
            self.projects.append({"name": project, "repos": []})
            for k, repo in enumerate(repos):
                branches = []
                request = requests.get('%s/rest/api/1.0/projects/%s/repos/%s/branches?limit=%s' %
                                       (self.url, project, repo, self.max_branch), auth=self.credentials)
                if "values" in request.json():
                    for branch in request.json()['values']:
                        branches.append(branch)
                # Only add repo if there are branches
                if len(branches) > 0:
                    self.projects[i]["repos"].append({"name": repo, "weight": 0, "branches": branches})
                    self.generated_repo_count += 1

    def weight_snapshot(self):
        if self.distribution == 'equal':
            return self.equal_weight()
        if self.distribution == "exponential":
            return self.exponential_weight()
        raise Exception("Unknown distribution '%s'" % self.distribution)

    def equal_weight(self):
        weight = 1.0 / self.generated_repo_count
        for project in self.projects:
            for repo in project["repos"]:
                repo["weight"] = weight

    def exponential_weight(self):
        # This prevent floats being written out in scientific/exponential notation
        encoder.FLOAT_REPR = lambda o: format(o, '.20f')
        weights = []
        total = 0
        for x in range(0, self.generated_repo_count):
            weight = self.random_exponential()
            weights.append(weight)
            total += weight
        normalize = 1.0 / total
        count = 0
        weight_count = 0
        for project in self.projects:
            for repo in project["repos"]:
                weight = weights[count] * normalize
                weight_count += weight
                repo["weight"] = weight
                count += 1
        # Confirm the total weight does equal 1
        print "Total weight count is %g" % weight_count

    def random_exponential(self):
        # The higher the distribution_factor the faster the fall off in values or the steeper the distribution.
        return -math.log(1 - (1 - math.exp(-self.distribution_factor)) * random.random()) / self.distribution_factor


@click.command()
@click.option('--url', help="Url of the bitbucket instance", default="http://localhost:7990/bitbucket")
@click.option('--key-file', help="File containing the keys of the users on the instance", default='Default')
@click.option('--username', help="Bitbucket admin user", default="admin")
@click.option('--password', help="User password", default="admin")
@click.option('--max-project', help="Maximum number of projects to include in the snapshot", default="100")
@click.option('--max-repo', help="Maximum number of repositories per project to include in the snapshot", default="100")
@click.option('--max-branch', help="Maximum number of branches per repository to include in the snapshot", default="5")
@click.option('--max-user', help="Maximum number of users to include in snapshot", default="500")
@click.option('--distribution', help="Weight distribution type", default="equal")
@click.option('--distribution-factor', help="Used by some distribution types to control the shape of the distribution",
              default="1")
@click.option('--description', help="Snapshot description", default="Default")
@click.option('--name', help="Snapshot name", default="Default")
@click.option('--aws', help="Set to true to scaffold the AWS specific snapshot configuration", default="false")
def command(url, key_file, username, password, max_branch, max_repo, max_project, max_user, distribution,
            distribution_factor, description, name, aws):
    Snapshot(url, key_file, username, password, max_project, max_repo, max_branch, max_user, distribution,
             distribution_factor, description, name, aws).generate()


if __name__ == '__main__':
    command()
