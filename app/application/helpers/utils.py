import json
import jsonlines
from .exceptions import *

# Input: path of the json/jsonlines file to be loaded
# Output: a list of dictionaries


def load_json(filepath):
    if filepath.lower().endswith(".json"):
        with open(f"{filepath}") as f:
            json_data = json.load(f)
            json_data = json.loads(json_data) if type(
                json_data) == str else json_data

        json_data = [json_data] if type(json_data) != list else json_data
        return json_data

    elif filepath.lower().endswith(".jl") or filepath.lower().endswith(".jsonl"):
        with jsonlines.open(f"{filepath}") as reader:
            json_data = [obj for obj in reader]

        return json_data

    else:
        raise InvalidFileException()
