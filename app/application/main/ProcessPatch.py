import re
import nltk

from collections import Counter, defaultdict
from copy import deepcopy
from application.helpers.utils import insert_individual_original_id
from nltk.tokenize import word_tokenize
from tqdm import tqdm

nltk.download('punkt', quiet=True)


class ProcessPatch():

    def __init__(self, newseries_original_id=1, change1_original_id=1, change2_original_id=1):
        self.newseries_original_id = newseries_original_id
        self.change1_original_id = change1_original_id
        self.change2_original_id = change2_original_id

    def organise_data_by_project(self, data):
        organised_data = defaultdict(list)

        for item in data:
            project_oid = item['project']
            organised_data[project_oid].append(item)

        return organised_data

    # This function is to create new series for patches, complementing missing series information
    # Patches that replied to the same email are considered as a new series of patches
    def series_grouping(self, patch_data: list):
        patch_data = deepcopy(patch_data)

        msgid_newseries_map = dict()
        newseries_collection = dict()
        ecosystem = patch_data[0]['original_id'].split('-')[0]

        for patch in patch_data:
            # skip if the patch does not contain in-reply-to id and its name does not indicate itself as in a series
            if patch['in_reply_to'] and self.__is_series_patch(patch['name']):

                in_reply_to = patch['in_reply_to']

                # Check if the patch contain multiple in-reply-to ids
                if type(in_reply_to) == list:
                    # Check if one of the in-reply-to ids has been associated with a new series id
                    # If so, associate that new series id to the rest of the in-reply-to id
                    for msg_id in in_reply_to:
                        if msg_id in msgid_newseries_map.keys():
                            # create a new original id
                            current_original_id = f'{ecosystem}-newseries-{msgid_newseries_map[msg_id]}'
                            patch['newseries'] = current_original_id
                            for msg_id2 in in_reply_to:
                                msgid_newseries_map[msg_id2] = msgid_newseries_map[msg_id]
                            break

                    # If not, associate a new new series id to all in-reply-to ids
                    if not patch['newseries']:
                        # create a new original id
                        current_original_id = f'{ecosystem}-newseries-{self.newseries_original_id}'
                        # associate new series original id to the patch
                        patch['newseries'] = current_original_id
                        # create a new new series
                        newseries = {
                            'original_id': current_original_id,
                            'cover_letter_msg_id': in_reply_to,
                            'project': patch['project'],
                            'submitter_identity': [patch['submitter_identity']],
                            'submitter_individual': [patch['submitter_individual']] if patch['submitter_individual'] else [],
                            'series': [patch['series']] if patch['series'] else []
                        }
                        newseries_collection[current_original_id] = newseries

                        # associate the new series id to all in-reply-to ids
                        for msg_id in in_reply_to:
                            msgid_newseries_map[msg_id] = self.newseries_original_id

                        self.newseries_original_id += 1

                    else:
                        # retrieve corresponding new series original id
                        current_original_id = f'{ecosystem}-newseries-{msgid_newseries_map[in_reply_to[0]]}'
                        # add new in-reply-to id to the new series
                        newseries_collection[current_original_id]['cover_letter_msg_id'].extend(
                            in_reply_to)

                        # add additional submitter identity to the new series
                        if patch['submitter_identity'] not in newseries_collection[current_original_id]['submitter_identity']:
                            newseries_collection[current_original_id]['submitter_identity'].append(
                                patch['submitter_identity'])

                        # add additional submitter individual to the new series
                        if patch['submitter_individual'] and patch['submitter_individual'] not in newseries_collection[current_original_id]['submitter_individual']:
                            newseries_collection[current_original_id]['submitter_individual'].append(
                                patch['submitter_individual'])

                        # add additional related series original id of the new series
                        if patch['series'] and patch['series'] not in newseries_collection[current_original_id]['series']:
                            newseries_collection[current_original_id]['series'].append(
                                patch['series'])

                # When the patch contain only one in-reply-to id
                # Check if the in-reply-to id has been associated with a new series id
                # If not, associate a new new series id to the in-reply-to id
                else:

                    # Check if the in-reply-to id has been associated with a new series original id
                    if in_reply_to in msgid_newseries_map.keys():
                        # retrieve corresponding new series original id
                        current_original_id = f'{ecosystem}-newseries-{msgid_newseries_map[in_reply_to]}'

                        # associate the new series original id to the patch
                        patch['newseries'] = current_original_id

                        # add additional submitter identity and individual and related series original id to the new series
                        if patch['submitter_identity'] not in newseries_collection[current_original_id]['submitter_identity']:
                            newseries_collection[current_original_id]['submitter_identity'].append(
                                patch['submitter_identity'])

                        if patch['submitter_individual'] and patch['submitter_individual'] not in newseries_collection[current_original_id]['submitter_individual']:
                            newseries_collection[current_original_id]['submitter_individual'].append(
                                patch['submitter_individual'])

                        if patch['series'] and patch['series'] not in newseries_collection[current_original_id]['series']:
                            newseries_collection[current_original_id]['series'].append(
                                patch['series'])
                    else:
                        # create a new new series original id
                        current_original_id = f'{ecosystem}-newseries-{self.newseries_original_id}'

                        # associate the new series original id to the patch
                        patch['newseries'] = current_original_id

                        # associate in-reply-to id to the new series original id
                        msgid_newseries_map[in_reply_to] = self.newseries_original_id

                        # create a new new series
                        newseries = {
                            'original_id': current_original_id,
                            'cover_letter_msg_id': [in_reply_to],
                            'project': patch['project'],
                            'submitter_identity': [patch['submitter_identity']],
                            'submitter_individual': [patch['submitter_individual']] if patch['submitter_individual'] else [],
                            'series': [patch['series']] if patch['series'] else []
                        }
                        newseries_collection[current_original_id] = newseries

                        self.newseries_original_id += 1

        # Create new series collection
        newseries_data = list(newseries_collection.values())
        for s in newseries_data:
            s['series'] = [] if s['series'] == [None] else s['series']
            s['inspection_needed'] = True if len(
                s['cover_letter_msg_id']) > 1 else False
            if len(s['cover_letter_msg_id']) == 1:
                s['cover_letter_msg_id'] = s['cover_letter_msg_id'][0]

        return patch_data, newseries_data

    # This function is to insert mailing list original id to patch or comment data
    def insert_mailinglist_id(self, mailinglist_data, target_data):
        msgid_to_orgid = {}

        for item in mailinglist_data:

            msgid_to_orgid[item['msg_id']] = item["original_id"]

        for item in target_data:
            if item['msg_id'] in msgid_to_orgid.keys():
                item['mailinglist'] = msgid_to_orgid[item['msg_id']]

    ##################################
    # Conservative grouping
    ##################################

    # This function is to execute conservative patch grouping
    def conservative_grouping(self, raw_data_patch):
        # Create a deep copy of inputted patch data so that the original one is not modified
        raw_data_patch = deepcopy(raw_data_patch)
        # Identify the ecosystem of the patch data
        ecosystem = raw_data_patch[0]['original_id'].split('-')[0]
        # Create bags of words and tokens of patch names and sort patches by their tokens and dates
        patch_data = self.__preprocess_raw_data_patch(raw_data_patch)

        # Patches of the same review process will be saved in the same group in the list
        conservative_groups = list()
        # Each visited patch is saved with the index number of the group in patch_groups
        visited_patches = dict()

        i = 0
        while i < len(patch_data):
            # Currenty visited patch
            patch_i = patch_data[i]

            # Skip if this patch contain no code changes, it will not be in the Change collection
            if not patch_i['code_diff']:
                i += 1
                continue

            # Get patch information
            bag_of_words_i = patch_i['bag_of_words']
            series_original_id_i = patch_i['series']
            newseries_original_id_i = patch_i['newseries']
            version_i = self.__extract_version_number(patch_i['name'])

            # Create new group for firstly visited patch
            new_conservative_group = {
                'patch_indexes': [i],
                'versions': [version_i],
                'bag_of_words': bag_of_words_i,
                'tokens': sorted(patch_i['tokens']),
                'state': [patch_i['state']],
                'commit_id': [patch_i['commit_ref']],
                'project': patch_i['project'],
                'submitters': [patch_i['submitter_identity']],
                'individuals': [patch_i['submitter_individual']],
                'series_original_ids': [series_original_id_i],
                'newseries_original_ids': [newseries_original_id_i],
            }
            conservative_groups.append(new_conservative_group)

            # Record visited patch
            original_id_i = patch_i['original_id']
            visited_patches[original_id_i] = len(conservative_groups) - 1

            # Patch with 0 token will not be grouped with other patches
            if len(patch_i['tokens']) == 0:
                i += 1
                continue

            # Compare patch_i with the remaining patches
            j = i + 1
            while j < len(patch_data):
                patch_j = patch_data[j]

                # Skip if this patch contain no code changes, it will not be in the Change collection
                if not patch_j['code_diff']:
                    j += 1
                    continue

                # Get patch information
                bag_of_words_j = patch_j['bag_of_words']
                series_original_id_j = patch_j['series']
                newseries_original_id_j = patch_j['newseries']

                # Compute token differences between patch i and patch j
                token_diff = (bag_of_words_i | bag_of_words_j) - \
                    (bag_of_words_i & bag_of_words_j)

                # Group patch i and patch j if the grouping criteria are met
                if (
                    len(token_diff) == 0
                    and self.__is_diff_series(series_original_id_i, series_original_id_j)
                    and self.__is_diff_series(newseries_original_id_i, newseries_original_id_j)
                ):
                    target_group_idx = visited_patches[original_id_i]
                    version_j = self.__extract_version_number(patch_j['name'])

                    conservative_groups[target_group_idx]['patch_indexes'].append(
                        j)
                    conservative_groups[target_group_idx]['versions'].append(
                        version_j)
                    conservative_groups[target_group_idx]['submitters'].append(
                        patch_j['submitter_identity'])
                    conservative_groups[target_group_idx]['individuals'].append(
                        patch_j['submitter_individual'])
                    conservative_groups[target_group_idx]['series_original_ids'].append(
                        series_original_id_j)
                    conservative_groups[target_group_idx]['newseries_original_ids'].append(
                        newseries_original_id_j)
                    conservative_groups[target_group_idx]['state'].append(
                        patch_j['state'])
                    conservative_groups[target_group_idx]['commit_id'].append(
                        patch_j['commit_ref'])

                    j += 1

                else:
                    break

            # The while loop has traversed to and stopped at patch j, and found that patch j is not in the same review process as patch i,
            # so the loop will start at patch j, and compare it with the remaining patches
            i = j

        # Create conservative change collection
        conservative_changes = self.__create_conservative_change(
            ecosystem, patch_data, conservative_groups)

        return patch_data, conservative_groups, conservative_changes

    # This function is to extract the version number of a patch (i.e. which version of the patch is)
    def __extract_version_number(self, patch_name):
        patch_name = patch_name.lower()
        indicator_part = re.findall(
            "^\[.*?\]\s*v\d+|\[.*?[,\s]+v\d+[,\s]+.*?\]|\[.*?[,\s]+v\d+\]|\[v\d+[,\s]+.*?\]|\(v\d+\)|\[v\d+\]|[\(\[]*patchv\d+[\)\]]*", patch_name)
        for item in indicator_part:
            indicator = re.search("v\d+", item)
            if indicator:
                version_number = re.search("\d+", indicator.group())
                return int(version_number.group())
        return -1

    # This function is to create bags of words for patch names
    def __create_bag_of_words(self, patch_name):
        patch_name = patch_name.lower()

        if re.findall("^\[.*?\]\s*v\d+.+", patch_name):
            patch_name = re.sub(r'\[.*?\]\s*v\d+', ' ', patch_name, 1)

        elif re.findall("^\[.*?\].+", patch_name):
            patch_name = re.sub(r'\[.*?\]', ' ', patch_name, 1)

        patch_words = re.sub(
            r'[\(\[]patch[\)\]]|\[*patchv\d+\]*|\d+/\d+\W|\[v\d+\]|\(v\d+\)|[^\w\s/-]', ' ', patch_name)

        # sort the tokens for quick comparison
        tokens = sorted(word_tokenize(patch_words))
        bag_of_words = Counter(tokens)

        return tokens, bag_of_words

    # This function is to preprocess patches before they are being grouped,
    # by creating bags of words for patches and sorting them by token and date
    def __preprocess_raw_data_patch(self, raw_data_patch):
        # create bag of words for each patch name
        for i in range(len(raw_data_patch)):
            patch_i = raw_data_patch[i]
            patch_i['tokens'], patch_i['bag_of_words'] = self.__create_bag_of_words(
                patch_i['name'])

        # sort patches
        return sorted(raw_data_patch, key=lambda x: (x['tokens'], x['date']))

    # This function is to check whether two patches belong to the same series
    def __is_diff_series(self, series_id1, series_id2):
        if series_id1 is None and series_id2 is None:
            return True

        return series_id1 != series_id2

    # This function is to create the conservative change collection
    def __create_conservative_change(self, ecosystem, patch_data, conservative_results):
        change1_collection = list()
        tmp_id_map = dict()
        for j in range(len(conservative_results)):
            group = conservative_results[j]

            is_accepted = True if 'accepted' in group['state'] else False
            commit_ids = list(set(group['commit_id']))
            if None in commit_ids:
                commit_ids.remove(None)

            project_original_id = group['project']
            submitter_identity_original_id = list(set(group['submitters']))
            submitter_individual_original_id = list(set(group['individuals']))

            series_original_id = list(set(group['series_original_ids']))
            if None in series_original_id:
                series_original_id.remove(None)

            newseries_original_id = list(set(group['newseries_original_ids']))
            if None in newseries_original_id:
                newseries_original_id.remove(None)

            if commit_ids and len(commit_ids) > 1:
                inspection_needed = True
            elif commit_ids and len(commit_ids) == 1:
                commit_ids = commit_ids[0]
                inspection_needed = False
            elif commit_ids == []:
                commit_ids = None
                inspection_needed = False
            elif len(group["tokens"]) == 0:
                inspection_needed == True

            tmp_dict = {
                'original_id': f'{ecosystem}-change1-{self.change1_original_id}',
                'is_accepted': is_accepted,
                'parent_commit_id': None,
                'merged_commit_id': commit_ids,
                'commit_date': None,
                'project': project_original_id,
                'submitter_identity': submitter_identity_original_id,
                'submitter_individual': submitter_individual_original_id,
                'series': series_original_id,
                'newseries': newseries_original_id,
                'patch': [patch_data[i]['original_id'] for i in group['patch_indexes']],
                'inspection_needed': inspection_needed,
            }

            tmp_id_map[f'{ecosystem}-change1-{self.change1_original_id}'] = j

            for patch_idx in group['patch_indexes']:
                if patch_data[patch_idx]['change1'] == None:
                    patch_data[patch_idx]['change1'] = f'{ecosystem}-change1-{self.change1_original_id}'
                else:
                    # label current change1 as inspection needed
                    tmp_dict['inspection_needed'] = True

                    # track the conflicting change1 and label it inpection needed
                    group_idx = tmp_id_map[patch_data[patch_idx]['change1']]
                    change1_collection[group_idx]['inspection_needed'] = True

            change1_collection.append(tmp_dict)
            self.change1_original_id += 1

        return change1_collection

    ##################################
    # Relaxed grouping
    ##################################

    # This function is to execute relaxed patch grouping
    def relaxed_grouping(self, raw_data_patch, progress_bar=True):
        # Identify the ecosystem of the patch data
        ecosystem = raw_data_patch[0]['original_id'].split('-')[0]
        # Execute conservative patch grouping
        patch_data, conservative_groups, conservative_changes = self.conservative_grouping(
            raw_data_patch)

        # Preprocess conservative patch groups before relaxed grouping
        organised_conservative_groups = self.__organise_patch_groups_by_token_len(
            conservative_groups)

        relaxed_groups = list()
        visited_groups = dict()

        token_lengths = sorted(organised_conservative_groups.keys())

        if progress_bar:
            pbar = tqdm(total=len(token_lengths) - 1)

        # This while loop is to compare groups with token length n and groups with token length n + 1 (one word difference)
        i = 0
        while i < len(token_lengths) - 1:
            # Patch groups with token length 0 will not be changed; consecutive token lengths are required
            if token_lengths[i] == 0 or token_lengths[i] + 1 != token_lengths[i + 1]:
                i += 1
                if progress_bar:
                    pbar.update(1)
                continue

            # Patch groups with token length n & patch groups with token length n + 1
            group_collection1 = organised_conservative_groups[token_lengths[i]]
            group_collection2 = organised_conservative_groups[token_lengths[i] + 1]

            # Comparison
            self.__relaxed_comparison(
                group_collection1, group_collection2, visited_groups, relaxed_groups, conservative_groups)

            i += 1
            if progress_bar:
                pbar.update(1)

        if progress_bar:
            pbar.close()

        # Create relaxed change collection
        relaxed_changes = self.__create_relaxed_change(
            ecosystem, patch_data, relaxed_groups)

        return patch_data, conservative_groups, relaxed_groups, conservative_changes, relaxed_changes

    # This funciton is to organise conservative patch groups (i.e. conservative changes) by their token length
    # Patch groups are temporarily stored together in one list if their token lengths are the same (patches in the same patch group share the same tokens)
    def __organise_patch_groups_by_token_len(self, groups):
        sorted_groups = defaultdict(list)
        for i in range(len(groups)):
            group_i = groups[i]
            group_token_length = len(group_i['tokens'])
            sorted_groups[group_token_length].append(deepcopy(group_i))
        return sorted_groups

    # This function is to organise patch groups with the same first/second token together
    def __organise_patch_groups_by_token(self, group_collection, token_position):
        orgainsed_collection = defaultdict(list)

        for group in group_collection:
            orgainsed_collection[group['tokens'][token_position]].append(group)

        return orgainsed_collection

    # This function executes the comparison logic of relaxed grouping
    def __relaxed_compare_patch_groups(self, orgainsed_collection, group_i, conservative_groups, visited_groups, relaxed_groups):
        group_i_idx = conservative_groups.index(group_i)
        token0_i = group_i['tokens'][0]
        bag_of_words_i = group_i['bag_of_words']
        series_original_id_i = group_i['series_original_ids']
        newseries_original_id_i = group_i['newseries_original_ids']
        versions_i = deepcopy(group_i['versions'])
        individual_i = group_i['individuals']

        j = 0
        group_be_compared = orgainsed_collection[token0_i]

        while group_be_compared and j < len(group_be_compared):
            group_j = group_be_compared[j]

            bag_of_words_j = group_j['bag_of_words']
            series_original_id_j = group_j['series_original_ids']
            newseries_original_id_j = group_j['newseries_original_ids']
            versions_j = deepcopy(group_j['versions'])
            individual_j = group_j['individuals']
            tokens_j = group_j['tokens']

            token_diff = (bag_of_words_i | bag_of_words_j) - \
                (bag_of_words_i & bag_of_words_j)

            target_group_idx = visited_groups[group_i_idx]

            # Merge two patch groups if the grouping criteria are met
            # The first condition is to avoid repetitively merged the same group when comparing the second token
            if (not set(group_j['patch_indexes']).issubset(set(relaxed_groups[target_group_idx]['patch_indexes']))
                and len(token_diff) == 1
                and bool(set(individual_i) & set(individual_j))
                and 'revert' not in list(token_diff.keys())[0].lower()
                and not self.__is_series_intersected(series_original_id_i, series_original_id_j)
                and not self.__is_series_intersected(newseries_original_id_i, newseries_original_id_j)
                    and not self.__is_version_intersected(versions_i, versions_j)):

                # Remove the merged group from the group collection being compared
                orgainsed_collection[token0_i].pop(j)

                # Update corresponding relaxed group information
                relaxed_groups[target_group_idx]['patch_indexes'].extend(
                    group_j['patch_indexes'])
                relaxed_groups[target_group_idx]['versions'].extend(
                    versions_j)
                relaxed_groups[target_group_idx]['series_original_ids'].extend(
                    series_original_id_j)
                relaxed_groups[target_group_idx]['newseries_original_ids'].extend(
                    newseries_original_id_j)
                relaxed_groups[target_group_idx]['bag_of_words'].append(
                    bag_of_words_j)
                relaxed_groups[target_group_idx]['tokens'].append(tokens_j)

                relaxed_groups[target_group_idx]['state'].extend(
                    group_j['state'])
                relaxed_groups[target_group_idx]['commit_id'].extend(
                    group_j['commit_id'])
                relaxed_groups[target_group_idx]['submitters'].extend(
                    group_j['submitters'])
                relaxed_groups[target_group_idx]['individuals'].extend(
                    group_j['individuals'])

                # Mark this patch group as visited
                group_j_idx = conservative_groups.index(group_j)
                visited_groups[group_j_idx] = target_group_idx
            else:
                j += 1

    # This function is to compare patch groups with token length n and patch groups with token length n + 1
    def __relaxed_comparison(self, group_collection1, group_collection2, visited_groups, relaxed_groups, conservative_groups):

        # Sort patch groups by tokens
        group_collection1 = sorted(
            deepcopy(group_collection1), key=lambda x: x['tokens'])
        group_collection2 = sorted(
            deepcopy(group_collection2), key=lambda x: x['tokens'])

        # Each patch group is organised into a group with the same 1st/2nd token
        orgainsed_collection2_token0 = self.__organise_patch_groups_by_token(
            group_collection2, 0)
        orgainsed_collection2_token1 = self.__organise_patch_groups_by_token(
            group_collection2, 1)

        for group_i in group_collection1:
            group_i_idx = conservative_groups.index(group_i)

            # If this group has not been compared and merged with other groups, create a new relaxed group for it
            if group_i_idx not in visited_groups.keys():
                relaxed_groups.append(
                    {
                        'patch_indexes': deepcopy(group_i['patch_indexes']),
                        'versions': deepcopy(group_i['versions']),
                        'bag_of_words': [deepcopy(group_i['bag_of_words'])],
                        'tokens': [deepcopy(group_i['tokens'])],
                        'series_original_ids': deepcopy(group_i['series_original_ids']),
                        'newseries_original_ids': deepcopy(group_i['newseries_original_ids']),

                        'state': deepcopy(group_i['state']),
                        'commit_id': deepcopy(group_i['commit_id']),
                        'project': group_i['project'],
                        'submitters': deepcopy(group_i['submitters']),
                        'individuals': deepcopy(group_i['individuals']),
                    }
                )
                visited_groups[group_i_idx] = len(relaxed_groups) - 1

            # We only need to compare the patch group with other patch groups whose token length is the same and whose first/second token is the same
            # First token is the same: they may have only one different token after the first token
            # Second token is the same: they may have only one different token as the first token
            # Third token is the same: they have two different tokens as the first and second tokens, which is over one word difference
            self.__relaxed_compare_patch_groups(
                orgainsed_collection2_token0, group_i, conservative_groups, visited_groups, relaxed_groups)

            self.__relaxed_compare_patch_groups(
                orgainsed_collection2_token1, group_i, conservative_groups, visited_groups, relaxed_groups)

    # This function is to create the relaxed change collection
    def __create_relaxed_change(self, ecosystem, patch_data, relaxed_groups):
        relaxed_changes = list()
        tmp_id_map = dict()

        for j in range(len(relaxed_groups)):
            group = relaxed_groups[j]
            is_accepted = True if 'accepted' in group['state'] else False

            commit_ids = list(set(group['commit_id']))
            if None in commit_ids:
                commit_ids.remove(None)

            current_original_id = f'{ecosystem}-change2-{self.change2_original_id}'
            project_original_id = group['project']
            submitter_identity_original_id = list(set(group['submitters']))
            submitter_individual_original_id = list(set(group['individuals']))

            series_original_id = list(set(group['series_original_ids']))
            if None in series_original_id:
                series_original_id.remove(None)

            newseries_original_id = list(set(group['newseries_original_ids']))
            if None in newseries_original_id:
                newseries_original_id.remove(None)

            if commit_ids and len(commit_ids) > 1:
                inspection_needed = True
            elif commit_ids and len(commit_ids) == 1:
                commit_ids = commit_ids[0]
                inspection_needed = False
            elif commit_ids == []:
                commit_ids = None
                inspection_needed = False

            tmp_dict = {
                'original_id': current_original_id,
                'is_accepted': is_accepted,
                'parent_commit_id': None,
                'merged_commit_id': commit_ids,
                'commit_date': None,
                'project': project_original_id,
                'submitter_identity': submitter_identity_original_id,
                'submitter_individual': submitter_individual_original_id,
                'series': series_original_id,
                'newseries': newseries_original_id,
                'patch': [patch_data[i]['original_id'] for i in group['patch_indexes']],
                'inspection_needed': inspection_needed,
            }

            tmp_id_map[current_original_id] = j

            for patch_idx in group['patch_indexes']:
                if patch_data[patch_idx]['change2'] == None:
                    patch_data[patch_idx]['change2'] = current_original_id
                else:
                    tmp_dict['inspection_needed'] = True

                    group_idx = tmp_id_map[patch_data[patch_idx]['change2']]
                    relaxed_changes[group_idx]['inspection_needed'] = True

            relaxed_changes.append(tmp_dict)
            self.change2_original_id += 1

        return relaxed_changes

    # Update conservative change (change1) and relaxed change (change2) original id in each comment
    def update_changeid_in_comment(self, change1_collection: list, change2_collection: list, comment_collection: list):

        change1_collection = deepcopy(change1_collection)
        change2_collection = deepcopy(change2_collection)
        comment_collection = deepcopy(comment_collection)

        mapping = defaultdict(list)
        for i in range(len(comment_collection)):
            comment = comment_collection[i]
            mapping[comment['patch']].append(i)

        for change1 in change1_collection:
            for patch_orgid in change1['patch']:
                for comment_collection_index in mapping[patch_orgid]:
                    comment_collection[comment_collection_index]['change1'] = change1['original_id']

        for change2 in change2_collection:
            for patch_orgid in change2['patch']:
                for comment_collection_index in mapping[patch_orgid]:
                    comment_collection[comment_collection_index]['change2'] = change2['original_id']

        return comment_collection

    # This function processes raw data of patch and comment and then does relaxed grouping, on a project level
    def patch_grouping(self, raw_data_patch: list, raw_data_comment: list, processed_data_individual: list, progress_bar=True):
        raw_data_patch = deepcopy(raw_data_patch)
        raw_data_comment = deepcopy(raw_data_comment)

        # create newseries
        raw_data_patch, data_newseries = self.series_grouping(raw_data_patch)

        # update individual oid in patches, comments, and newseries
        raw_data_patch, raw_data_comment, processed_data_newseries = [
            insert_individual_original_id(processed_data_individual, data)
            for data in [raw_data_patch, raw_data_comment, data_newseries]
        ]

        # relaxed grouping
        processed_data_patch, _, _, conservative_changes, relaxed_changes = self.relaxed_grouping(
            raw_data_patch, progress_bar)

        # update change1 and change2 ids in comments
        processed_data_comment = self.update_changeid_in_comment(
            conservative_changes, relaxed_changes, raw_data_comment)

        return processed_data_newseries, processed_data_patch, processed_data_comment, conservative_changes, relaxed_changes

    # This function is to check if the patch name indicates the patch belongs to a series
    def __is_series_patch(self, patch_name):
        series_number = re.search('\d+/\d+', patch_name, re.IGNORECASE)
        return bool(series_number)

    # This function is to check if the version numbers in two patch groups are intersected
    def __is_version_intersected(self, list_i, list_j):
        if set(list_i) & set(list_j) == {-1}:
            return False
        return bool(set(list_i) & set(list_j))

    # This function is to check if the series original ids in two patch groups are intersected
    def __is_series_intersected(self, list_i, list_j):
        if set(list_i) & set(list_j) == {None}:
            return False
        return bool(set(list_i) & set(list_j))
