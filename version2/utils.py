import json


def load():
    with open('flow3.json') as outstream:
        data = json.loads(outstream.read())

    return data
