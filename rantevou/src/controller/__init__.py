import json
import pathlib

PATH = pathlib.Path(__file__).parent.parent.parent.parent / "config.json"


def get_config():
    with PATH.open("r") as f:
        return json.load(f)
