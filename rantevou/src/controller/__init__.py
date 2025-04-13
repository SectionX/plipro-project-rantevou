import json
import pathlib

PATH = pathlib.Path(__file__).parent.parent.parent.parent / "settings.json"

cfg = None


def get_config():
    global cfg
    if cfg is None:
        with PATH.open("r") as f:
            cfg = json.load(f)
    return cfg
