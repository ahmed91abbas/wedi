import json

def open_json(filepath):
    with open(filepath, "r") as infile:
        return json.load(infile)

def save_json(filepath, data):
    with open(filepath, "w") as outfile:
        outfile.write(json.dumps(data, indent=4))