#!/usr/bin/env python

import json

import click
import requests


class AddUsers:
    def __init__(self, count, keyfile, hostname, username, password):
        self.count = int(count)
        self.auth = (username, password)
        self.hostname = hostname
        self.keyfile = keyfile

    def generate(self):
        key_pairs = json.load(open('../data/keys/%s.json' % self.keyfile))
        available_keys = key_pairs['count']
        if int(available_keys) < self.count:
            raise Exception("Not enough keys. Specified %d new users, %d keys available" % (available_keys, self.count))

        for i in range(self.count):
            add_user_url = 'http://%(base_url)s/rest/api/1.0/admin/users?name=%(name)s&password=%(password)s&' \
                           'displayName=%(display_name)s&emailAddress=%(email_address)s' \
                           '&true' % {'base_url': self.hostname,
                                      'name': 'user_%s' % i,
                                      'password': 'test',
                                      'email_address': 'foo_%s@bar.com' % i,
                                      'display_name': 'display_name_%s' % i}
            print add_user_url
            response = requests.post(
                add_user_url, auth=self.auth, headers={"Content-Type": "application/json"})
            print "Adding user #%d using url %s response { status code:%s, text:%s }" % (i, add_user_url,
                                                                                         response.status_code,
                                                                                         response.text)

            add_key_url = 'http://%(base_url)s/rest/ssh/1.0/keys?user=%(username)s' % {'base_url': self.hostname,
                                                                                       'username': 'user_%s' % i}

            public_key = key_pairs['key_pairs'][i]['public_key']
            print public_key
            response = requests.post(add_key_url,
                                     auth=self.auth,
                                     data=json.dumps({'text': public_key}),
                                     headers={"Content-Type": "application/json"})

            print add_key_url
            print response.status_code
            print response.text
        print "Finished generating adding %d users with key pairs to %s" % (self.count, self.hostname)


@click.command()
@click.option('--count', help="Number of keys to generate", default=100)
@click.option('--keyfile', help="Key file name", required=True)
@click.option('--hostname', help="Hostname of bitbucket system", required=True)
@click.option('--username', help="Admin username", required=True)
@click.option('--password', help="Admin password", required=True)
def command(count, keyfile, hostname, username, password):
    AddUsers(count, keyfile, hostname, username, password).generate()


if __name__ == '__main__':
    command()
