import argparse
from collections import defaultdict
import time
from application.main.ProcessData import ProcessData
from application.helpers.utils import *

# TODO
# group newseries -> to record newseries oid in patches x
# import processed individual data, patch data, comment data x
# update individual oid in patches and newseries x
# start grouping patches

###############################################
# currently only consider a single project case
###############################################

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--ecosystem')

args = parser.parse_args()

RESULTS_DIR = '/Users/mingzhaoliang/projects/msr/Code-Review-Mining/results/'
RAW_DATA_DIR = '/Users/mingzhaoliang/projects/msr/raw-data/'
ECOSYSTEM = args.ecosystem


def organise_data_by_project(data):
    organised_data = defaultdict(list)

    for item in data:
        project_oid = item['project']
        organised_data[project_oid].append(item)

    return organised_data


def grouping_by_project(process_data_object, project_data_individual, project_data_patch, project_data_comment):
    # group newseries
    project_data_patch, project_data_newseries = process_data_object.group_series(
        project_data_patch)

    # update individual oid in patches, comments, and newseries
    data_patch = process_data_object.insert_individual_original_id(
        project_data_individual, project_data_patch)
    data_comment = process_data_object.insert_individual_original_id(
        project_data_individual, project_data_comment)
    processed_data_newseries = process_data_object.insert_individual_original_id(
        project_data_individual, project_data_newseries)

    # group patches
    processed_data_patch, processed_data_comment, conservative_changes, relaxed_changes = process_data_object.patch_grouping(
        data_patch, data_comment)

    return processed_data_newseries, processed_data_patch, processed_data_comment, conservative_changes, relaxed_changes


def output_data(target_data, target_data_type):
    with jsonlines.open(f'{RESULTS_DIR}{ECOSYSTEM}/{ECOSYSTEM}_{target_data_type}.jl', 'w') as writer:
        writer.write_all(target_data)


if __name__ == '__main__':
    # get file paths
    processed_data_individual_path = f'{RESULTS_DIR}{ECOSYSTEM}/{ECOSYSTEM}_individual.jl'
    raw_data_patch_path = f'{RAW_DATA_DIR}{ECOSYSTEM}/{ECOSYSTEM}_patch.jl'
    raw_data_comment_path = f'{RAW_DATA_DIR}{ECOSYSTEM}/{ECOSYSTEM}_comment.jl'

    # load data
    # imported data contains all projects of an ecosystem
    processed_data_individual = load_json(processed_data_individual_path)
    raw_data_patch = load_json(raw_data_patch_path)
    raw_data_comment = load_json(raw_data_comment_path)

    # organise data by projects
    organised_processed_data_individual = organise_data_by_project(
        processed_data_individual)
    organised_raw_data_patch = organise_data_by_project(raw_data_patch)
    organised_raw_data_comment = organise_data_by_project(raw_data_comment)

    # instantiate process_data class
    process_data = ProcessData()

    processed_data_newseries, processed_data_patch, processed_data_comment, conservative_changes, relaxed_changes = [], [], [], [], []
    processed_data = [processed_data_newseries, processed_data_patch,
                      processed_data_comment, conservative_changes, relaxed_changes]

    # iterate each project
    st = time.time()
    project_oids = list(organised_raw_data_patch.keys())
    for project_oid in project_oids:
        start_time = time.time()

        current_data_individual = organised_processed_data_individual[project_oid]
        current_data_patch = organised_raw_data_patch[project_oid]
        current_data_comment = organised_raw_data_comment[project_oid]

        # processed_data_newseries, processed_data_patch, processed_data_comment, conservative_changes, relaxed_changes
        results = grouping_by_project(
            process_data,
            current_data_individual,
            current_data_patch,
            current_data_comment
        )

        [processed_data[i].extend(results[i]) for i in range(len(results))]

        end_time = time.time()
        print(f'{project_oid}: {(end_time - start_time) / 60: .2f} min')
        print()

    et = time.time()
    print(f'total time: {(end_time - start_time) / 60: .2f} min')
    data_types = ['newseries', 'patch', 'comment', 'change1', 'change2']
    [output_data(data, data_type)
     for data, data_type in zip(processed_data, data_types)]
