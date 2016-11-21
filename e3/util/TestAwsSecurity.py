#!/usr/bin/env python

"""
This exists for testing purposes to ensure that the Security implementation works.
"""

import logging.config
import os

import sys
from pprint import pprint

if __name__ == "__main__":
    # Add .. to the current PYTHON_PATH
    script_folder = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(script_folder, ".."))

    from common.E3 import E3
    from provisioning.AtlassianAwsSecurity import AtlassianAwsSecurity
    e3_config = E3()
    logging.config.fileConfig(e3_config.get_logging_conf())
    sec = AtlassianAwsSecurity()
    metadata = sec.load()
    pprint(metadata)
