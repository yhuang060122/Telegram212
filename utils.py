import json
from types import SimpleNamespace

def to_json(obj):
    res = json.dumps(obj, default=lambda o: o.__dict__)
    return res

def from_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        f.close()
        return data

def print_as_json(obj):
    print(to_json(obj))