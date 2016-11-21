#!/usr/bin/env python

import hashlib
import json
import os
import sys

import click
from Crypto.PublicKey import RSA


class KeyGenerator:
    def __init__(self, key_count, name):
        self.key_count = key_count
        self.name = name
        self.output_file = os.path.join("/home/ec2-user/" + name + ".json")

    def generate(self):
        output = {}
        output['count'] = self.key_count
        output['key_pairs'] = []
        for i in range(0, self.key_count):
            key_pair = RSA.generate(2048)
            public = key_pair.publickey().exportKey("OpenSSH")
            private = key_pair.exportKey("PEM")

            output['key_pairs'].append({'private_key': private, 'public_key': public})
            print "%s keys generated" % (i + 1)
            with open(self.output_file, 'w') as jsonFile:
                json.dump(output, jsonFile, indent=4, sort_keys=True)

    def write_private_key(self, key):
        name = hashlib.sha1(key).hexdigest() + ".pem"
        path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "../../")), "e3-home", "keys/", name)
        key_file = open(path, "w")
        key_file.write(key)
        key_file.close()
        return name


@click.command()
@click.option('--key-count', help="Number of keys required", default=3)
@click.option('--name', help="Name of this key file", default="Default")

def command(key_count, name):
    KeyGenerator(key_count, name).generate()


if __name__ == '__main__':
    command()
