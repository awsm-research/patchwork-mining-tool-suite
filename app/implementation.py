import argparse
import time
import jsonlines
from application.main.ProcessPatch import ProcessPatch
from application.main.ProcessIdentity import ProcessIdentity
from application.main.ProcessMailingList import ProcessMailingList
from application.helpers.utils import *

# add arguments
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--ecosystem')
parser.add_argument('-ra', '--raw_data_path')
parser.add_argument('-re', '--result_path')

# parse arguments
args = parser.parse_args()
ECOSYSTEM = args.ecosystem
RAW_DATA_DIR = args.raw_data_path if args.raw_data_path else './'
RESULTS_DIR = args.result_path if args.result_path else './'


def output_data(target_data, target_data_type):
    with jsonlines.open(f'{RESULTS_DIR}{ECOSYSTEM}/{ECOSYSTEM}_{target_data_type}.jl', 'w') as writer:
        writer.write_all(target_data)


if __name__ == '__main__':
    ###############
    # process mailing list data
    ###############

    raw_data_mailinglist = f'{RAW_DATA_DIR}{ECOSYSTEM}/{ECOSYSTEM}_mailinglist.jl'

    process_mailinglist = ProcessMailingList()

    processed_data_mailinglist = process_mailinglist.organise_data(
        raw_data_mailinglist)

    output_data(processed_data_mailinglist, 'mailinglist')

    ###############
    # group identities
    ###############

    # get file paths
    raw_data_identity_path = f'{RAW_DATA_DIR}{ECOSYSTEM}/{ECOSYSTEM}_identity.jl'

    # load data
    raw_data_identity = load_json(raw_data_identity_path)

    # instantiate process_identity class
    process_identity = ProcessIdentity()

    # organise data by projects
    organised_raw_data_identity = process_identity.organise_identity_data_by_project(
        raw_data_identity)

    # group identities
    processed_data_individual = []

    for project_oid, data in organised_raw_data_identity.items():
        current_data_individual = process_identity.identity_grouping(
            data, project_oid)

        processed_data_individual.extend(current_data_individual)

    output_data(processed_data_individual, 'individual')

    # update individual oid in series data
    raw_data_series_path = f'{RAW_DATA_DIR}{ECOSYSTEM}/{ECOSYSTEM}_series.jl'
    raw_data_series = load_json(raw_data_series_path)

    processed_data_series = insert_individual_original_id(
        processed_data_individual, raw_data_series)
    output_data(processed_data_individual, 'series')

    ###############
    # group patches
    ###############

    # get file paths
    processed_data_individual_path = f'{RESULTS_DIR}{ECOSYSTEM}/{ECOSYSTEM}_individual.jl'
    processed_data_mailinglist_path = f'{RESULTS_DIR}{ECOSYSTEM}/{ECOSYSTEM}_mailinglist.jl'

    raw_data_patch_path = f'{RAW_DATA_DIR}{ECOSYSTEM}/{ECOSYSTEM}_patch.jl'
    raw_data_comment_path = f'{RAW_DATA_DIR}{ECOSYSTEM}/{ECOSYSTEM}_comment.jl'

    # load data
    # imported data contains all projects of an ecosystem
    processed_data_individual = load_json(processed_data_individual_path)
    raw_data_patch = load_json(raw_data_patch_path)
    raw_data_comment = load_json(raw_data_comment_path)
    processed_data_mailinglist = process_mailinglist.organise_data_by_project(
        load_json(processed_data_mailinglist_path))

    # instantiate process_patch class
    process_patch = ProcessPatch()

    # organise data by projects
    organised_processed_data_individual, organised_raw_data_patch, organised_raw_data_comment = [
        process_patch.organise_data_by_project(data)
        for data in [processed_data_individual, raw_data_patch, raw_data_comment]
    ]

    # initialise variables
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
        results = process_patch.patch_grouping(
            current_data_patch, current_data_comment, current_data_individual)

        # insert mailing list orginal id to patch data
        process_patch.insert_mailinglist_id(
            processed_data_mailinglist[project_oid], results[1])

        # insert mailing list orginal id to comment data
        process_patch.insert_mailinglist_id(
            processed_data_mailinglist[project_oid], results[2])

        # store newly processed project data
        [processed_data[i].extend(results[i]) for i in range(len(results))]

        end_time = time.time()
        print(f'{project_oid}: {(end_time - start_time) / 60: .2f} min')
        print()

    et = time.time()
    print(f'total time: {(et - st) / 60: .2f} min')
    data_types = ['newseries', 'patch', 'comment', 'change1', 'change2']
    [output_data(data, data_type)
     for data, data_type in zip(processed_data, data_types)]
