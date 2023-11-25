import argparse
from application.helpers.utils import *
from application.main.AccessData import AccessData

# add arguments
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--ecosystem')
parser.add_argument('-re', '--result_path')

# parse arguments
args = parser.parse_args()
ECOSYSTEM = args.ecosystem
RESULTS_DIR = args.result_path if args.result_path else './'


def post_data(class_object, data, item_type):
    if item_type in ["patch", "comment"]:
        for item in data:
            if item["msg_content"]:
                item["msg_content"] = item["msg_content"].replace("\u0000", "")
    elif item_type == "mailinglist":
        for item in data:
            if item["content"]:
                item["content"] = item["content"].replace("\u0000", "")

    class_object.insert_data(data, item_type)


if __name__ == "__main__":

    access_data = AccessData()

    for item_type in ['identity', 'project', 'mailinglist', 'individual', 'series', 'newseries', 'change1', 'change2', 'patch', 'comment']:
        print("==================================================\n")
        print(item_type)
        current_data = load_json(
            f"{RESULTS_DIR}{ECOSYSTEM}/{ECOSYSTEM}_{item_type}.jl")
        post_data(access_data, current_data, item_type)
