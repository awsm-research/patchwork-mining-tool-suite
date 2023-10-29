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


# This method is to update the individual_original_id in series, newseries, patch, and comment collection
# It should be called after the function of grouping identities is implemented

def insert_individual_original_id(individual_data: list, target_data: list):

    # map identity original id to individual original id
    identity_to_individual = dict()
    for individual in individual_data:
        # one individual id contains one or multiple identity original ids
        identity_oids = individual['identity']
        for identity_oid in identity_oids:
            identity_to_individual[identity_oid] = individual['original_id']

    for item in target_data:
        if type(item['submitter_individual']) == list:
            for submitter_identity_oid in item['submitter_identity']:
                item['submitter_individual'].append(
                    identity_to_individual[submitter_identity_oid])
        else:
            item['submitter_individual'] = identity_to_individual[item['submitter_identity']]

    return target_data
