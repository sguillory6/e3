import json


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
    "decode_json", "encode_json", "load_json", "save_json"
]
