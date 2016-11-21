#!/usr/bin/env python

import json
import os
import sys

import click
from Crypto.PublicKey import RSA


class KeyGen:
    def __init__(self, count, name):
        self.count = count
        self.name = name
        self.output_file = os.path.join(os.path.abspath(
            os.path.join(os.path.dirname(sys.argv[0]), "../")), "data", "keys/", name + ".json")

    def generate(self):
        key_pairs = []
        keys = {"name": self.name, "count": self.count, "key_pairs": key_pairs}
        for i in range(self.count):
            key_pair = RSA.generate(2048)
            key_pairs.append({"public_key": key_pair.publickey().exportKey("OpenSSH"),
                              "private_key": key_pair.exportKey("PEM")})

        with open(self.output_file, 'w') as jsonFile:
            json.dump(keys, jsonFile, indent=4, sort_keys=True)

        print "Finished generating %d keys written to %s" % (self.count, self.output_file)


@click.command()
@click.option('--count', help="Number of keys to generate", default=100)
@click.option('--name', help="Snapshot name", required=True)
def command(count, name):
    KeyGen(count, name).generate()


if __name__ == '__main__':
    command()
