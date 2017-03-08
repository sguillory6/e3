import json
import sys


def load_script(script_name):
    script = script_name
    class_name = script
    if '.' in script:
        class_name = script.split('.').pop()
    test_data_provider_class = getattr(sys.modules[script], class_name)
    return test_data_provider_class


def decode_json(s):
    try:
        return json.loads(s)
    except StandardError:
        return {}


def encode_json(json_dict):
    return json.dumps(json_dict)


def load_json(path):
    try:
        with open(path, "r") as json_file:
            return json.load(json_file)
    except StandardError:
        return {}


def save_json(path, json_dict):
    try:
        with open(path, "w") as json_file:
            json.dump(json_dict, json_file, indent=2)
            return True
    except StandardError:
        return False


__all__ = [
    "load_script", "decode_json", "encode_json", "load_json", "save_json"
]
