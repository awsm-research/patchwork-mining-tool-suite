from collections import Counter, defaultdict
from copy import deepcopy
import re
import time
import nltk

from nltk.tokenize import word_tokenize

nltk.download('punkt', quiet=True)


class ProcessData():

    def __init__(self, newseries_original_id=1, change1_original_id=1, change2_original_id=1, individual_original_id=1):
        self.newseries_original_id = newseries_original_id
        self.change1_original_id = change1_original_id
        self.change2_original_id = change2_original_id
        self.individual_original_id = individual_original_id

    def __get_distinct_identities(self, identity_data: list):
        new_data = defaultdict(list)
        occurred_identities = list()
        for item in identity_data:
            if item not in occurred_identities:
                new_data[item['project']].append(item)
                occurred_identities.append(item)

        return new_data

    def __group_identities_by_project(self, identity_data: list, project: str):

        ecosystem = identity_data[0]['original_id'].split('-')[0]
        email_dict = dict()
        name_dict = dict()
        individual_dict = defaultdict(lambda: defaultdict(list))

        idx = 0

        # list for account with empty/null name/email
        identity_with_empty_name = list()
        identity_with_empty_email = list()

        for i in range(len(identity_data)):
            identity = identity_data[i]
            identity_email = identity['email']
            identity_name = identity['name']
            identity_orgid = identity['original_id']

            if not identity_name:
                identity_with_empty_name.append(
                    (i, identity_orgid, identity_email))
            elif not identity_email:
                identity_with_empty_email.append(
                    (i, identity_orgid, identity_name))

            elif identity_email not in email_dict.keys() and identity_name not in name_dict.keys():
                individual_dict[idx]['email_list'].append(identity_email)
                individual_dict[idx]['name_list'].append(identity_name)
                individual_dict[idx]['original_id_list'].append(identity_orgid)

                email_dict[identity_email] = idx
                name_dict[identity_name] = idx

                idx += 1

            elif identity_email in email_dict.keys() and identity_name not in name_dict.keys():
                target_idx = email_dict[identity_email]
                name_dict[identity_name] = target_idx
                individual_dict[target_idx]['name_list'].append(identity_name)
                individual_dict[target_idx]['original_id_list'].append(
                    identity_orgid)

            elif identity_email not in email_dict.keys() and identity_name in name_dict.keys():
                target_idx = name_dict[identity_name]
                email_dict[identity_email] = target_idx
                individual_dict[target_idx]['email_list'].append(
                    identity_email)
                individual_dict[target_idx]['original_id_list'].append(
                    identity_orgid)

            elif identity_email in email_dict.keys() and identity_name in name_dict.keys():
                if email_dict[identity_email] != name_dict[identity_name]:
                    email_dict_idx = email_dict[identity_email]
                    name_dict_idx = name_dict[identity_name]

                    email_list_to_move = individual_dict[name_dict_idx]['email_list']
                    name_list_to_move = individual_dict[name_dict_idx]['name_list']
                    orgid_list_to_move = individual_dict[name_dict_idx]['original_id_list']

                    for email in email_list_to_move:
                        email_dict[email] = email_dict_idx
                    for name in name_list_to_move:
                        name_dict[name] = email_dict_idx

                    individual_dict[email_dict_idx]['email_list'].extend(
                        email_list_to_move)
                    individual_dict[email_dict_idx]['name_list'].extend(
                        name_list_to_move)
                    individual_dict[email_dict_idx]['original_id_list'].extend(
                        orgid_list_to_move)

                    individual_dict[email_dict_idx]['name_list'].append(
                        identity_name)
                    individual_dict[email_dict_idx]['original_id_list'].append(
                        identity_orgid)

                    individual_dict[name_dict_idx] = None
                else:
                    target_idx = email_dict[identity_email]
                    individual_dict[target_idx]['original_id_list'].append(
                        identity_orgid)

        for _, orgid, email in identity_with_empty_name:
            if email in email_dict.keys():
                if orgid not in individual_dict[email_dict[email]]['original_id_list']:
                    individual_dict[email_dict[email]
                                    ]['original_id_list'].append(orgid)

            else:
                email_dict[email] = idx
                individual_dict[idx]['email_list'].append(email)
                individual_dict[idx]['original_id_list'].append(orgid)

                idx += 1

        for _, orgid, name in identity_with_empty_email:
            if name in name_dict.keys():
                if orgid not in individual_dict[name_dict[name]]['original_id_list']:
                    individual_dict[name_dict[name]
                                    ]['original_id_list'].append(orgid)

            else:
                name_dict[name] = idx
                individual_dict[idx]['name_list'].append(name)
                individual_dict[idx]['original_id_list'].append(orgid)

                idx += 1

        individual_collection = list()

        # update individual original id in identity collection
        for _, individual_info in individual_dict.items():
            if individual_info:
                original_id_list = individual_info['original_id_list']

                individual_collection.append(
                    {
                        'original_id': f'{ecosystem}-individual-{self.individual_original_id}',
                        'project': project,
                        'identity': original_id_list,
                    }
                )

                self.individual_original_id += 1

        return individual_collection

    def group_identities(self, identity_data: list):
        identity_data_by_project = self.__get_distinct_identities(
            identity_data)

        individual_data = list()

        for project, identity_list in identity_data_by_project.items():
            curr_individual_data = self.__group_identities_by_project(
                identity_list, project)

            individual_data.extend(curr_individual_data)

        return individual_data

    # This method is to update the individual_original_id in series, newseries, patch, and comment collection
    # It should be called after the function of grouping identities is implemented

    def update_individual_original_id(self, individual_data: list, collection: list):
        # map identity original id to individual original id
        identity_individual_map = defaultdict(lambda: defaultdict(str))
        for item in individual_data:
            project = item["project"]
            for item_identity_orgid in item["identity"]:
                identity_individual_map[project][item_identity_orgid] = item['original_id']

        for document in collection:
            if type(document['submitter_individual']) == list:
                for submitter in document['submitter_identity']:
                    document['submitter_individual'].append(
                        identity_individual_map[document['project']][submitter])
            else:
                document['submitter_individual'] = identity_individual_map[document['project']
                                                                           ][document['submitter_identity']]

        return collection

    def group_series(self, patch_data: list):
        patch_data = deepcopy(patch_data)

        # map msg_id to newseries_original_id
        msgid_newseries_map = dict()

        newseries_collection = dict()
        ecosystem = patch_data[0]['original_id'].split('-')[0]

        for patch in patch_data:
            if patch['in_reply_to'] and self.__is_series_patch(patch['name']):
                in_reply_to = patch['in_reply_to']

                if type(in_reply_to) == list:
                    for msg_id in in_reply_to:
                        if msg_id in msgid_newseries_map.keys():
                            current_original_id = f'{ecosystem}-newseries-{msgid_newseries_map[msg_id]}'
                            patch['newseries'] = current_original_id
                            for msg_id2 in in_reply_to:
                                msgid_newseries_map[msg_id2] = msgid_newseries_map[msg_id]
                            break

                    if not patch['newseries']:
                        current_original_id = f'{ecosystem}-newseries-{self.newseries_original_id}'
                        patch['newseries'] = current_original_id

                        newseries = {
                            'original_id': current_original_id,
                            'cover_letter_msg_id': in_reply_to,
                            'project': patch['project'],
                            'submitter_identity': [patch['submitter_identity']],
                            'submitter_individual': [patch['submitter_individual']] if patch['submitter_individual'] else [],
                            'series': [patch['series']] if patch['series'] else []
                        }
                        newseries_collection[current_original_id] = newseries

                        for msg_id in in_reply_to:
                            msgid_newseries_map[msg_id] = self.newseries_original_id

                        self.newseries_original_id += 1

                    else:
                        current_original_id = f'{ecosystem}-newseries-{msgid_newseries_map[in_reply_to[0]]}'

                        newseries_collection[current_original_id]['cover_letter_msg_id'].extend(
                            in_reply_to)

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

                    if in_reply_to in msgid_newseries_map.keys():
                        current_original_id = f'{ecosystem}-newseries-{msgid_newseries_map[in_reply_to]}'

                        patch['newseries'] = current_original_id
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
                        current_original_id = f'{ecosystem}-newseries-{self.newseries_original_id}'
                        patch['newseries'] = current_original_id
                        msgid_newseries_map[in_reply_to] = self.newseries_original_id

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

        newseries_data = list(newseries_collection.values())

        for s in newseries_data:
            s['series'] = [] if s['series'] == [None] else s['series']
            s['inspection_needed'] = True if len(
                s['cover_letter_msg_id']) > 1 else False
            if len(s['cover_letter_msg_id']) == 1:
                s['cover_letter_msg_id'] = s['cover_letter_msg_id'][0]

        return patch_data, newseries_data

    # This function is to group patches based on the criteria in step 1
    # It should be called after newseries collection is created

    def __create_bag_of_words(self, patch_name):
        patch_name = patch_name.lower()

        # case 1: [<header>]v1<main title>
        if re.findall("^\[.*?\]\s*v\d+.+", patch_name):
            # replace the content in the first bracket
            patch_name = re.sub(r'\[.*?\]\s*v\d+', ' ', patch_name, 1)

        # case 2: [<header>]<main title>
        elif re.findall("^\[.*?\].+", patch_name):
            # replace the content in the first bracket
            patch_name = re.sub(r'\[.*?\]', ' ', patch_name, 1)

        # replace patchv1, <series number>, [v1], (v1), <punctuations>
        patch_words = re.sub(
            r'[\(\[]patch[\)\]]|\[*patchv\d+\]*|\d+/\d+\W|\[v\d+\]|\(v\d+\)|[^\w\s/-]', ' ', patch_name)

        # sort the tokens for quick comparison
        tokens = sorted(word_tokenize(patch_words))
        bag_of_words = Counter(tokens)

        return tokens, bag_of_words

    def __preprocess_raw_data_patch(self, raw_data_patch):
        # create bag of word for each patch title
        for i in range(len(raw_data_patch)):
            patch_i = raw_data_patch[i]
            patch_i['tokens'], patch_i['bag_of_words'] = self.__create_bag_of_words(
                patch_i['name'])

        # sort patches
        return sorted(raw_data_patch, key=lambda x: (x['tokens'], x['date']))

    def __is_diff_series(self, series_id1, series_id2):
        if series_id1 is None and series_id2 is None:
            return True

        return series_id1 != series_id2

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

    def conservative_grouping(self, raw_data_patch):
        raw_data_patch = deepcopy(raw_data_patch)
        ecosystem = raw_data_patch[0]['original_id'].split('-')[0]
        patch_data = self.__preprocess_raw_data_patch(raw_data_patch)

        # patches of the same review process will be saved in the same group in the list
        conservative_groups = list()
        # each visited patch is saved with the index number of the group in patch_groups
        visited_patches = dict()

        i = 0
        while i < len(patch_data):
            # currenty visited patch
            patch_i = patch_data[i]

            # skip if this patch contain no code changes, it will not be in the Change dataset
            if not patch_i['code_diff']:
                i += 1
                continue

            # create a new conservative group for the visited patch
            bag_of_words_i = patch_i['bag_of_words']
            series_original_id_i = patch_i['series']
            newseries_original_id_i = patch_i['newseries']
            version_i = self.__extract_version_number(patch_i['name'])

            # create new group for firstly visited patch
            new_conservative_group = {
                'patch_indexes': [i],
                'versions': [version_i],
                'bag_of_words': bag_of_words_i,
                'tokens': sorted(patch_i['tokens']),
                # 'tokens2': tokens_i[1:],
                'state': [patch_i['state']],
                'commit_id': [patch_i['commit_ref']],
                'project': patch_i['project'],
                'submitters': [patch_i['submitter_identity']],
                'individuals': [patch_i['submitter_individual']],
                'series_original_ids': [series_original_id_i],
                'newseries_original_ids': [newseries_original_id_i],
            }
            conservative_groups.append(new_conservative_group)

            # record visited patch
            original_id_i = patch_i['original_id']
            visited_patches[original_id_i] = len(conservative_groups) - 1

            # patch with 0 token will not be grouped with other patches
            if len(patch_i['tokens']) == 0:
                i += 1
                continue

            # compare patch_i with the remaining patches
            j = i + 1
            while j < len(patch_data):
                patch_j = patch_data[j]

                if not patch_j['code_diff']:
                    j += 1
                    continue

                bag_of_words_j = patch_j['bag_of_words']
                series_original_id_j = patch_j['series']
                newseries_original_id_j = patch_j['newseries']

                # compute token differences
                token_diff = (bag_of_words_i | bag_of_words_j) - \
                    (bag_of_words_i & bag_of_words_j)

                # check grouping criteria
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

            i = j

        conservative_changes = self.__create_conservative_change(
            ecosystem, patch_data, conservative_groups)

        return patch_data, conservative_groups, conservative_changes

    def __organise_patch_groups_by_token_len(self, groups):
        sorted_groups = defaultdict(list)
        for i in range(len(groups)):
            group_i = groups[i]
            group_token_length = len(group_i['tokens'])
            sorted_groups[group_token_length].append(deepcopy(group_i))
        return sorted_groups

    def __organise_patch_groups_by_token(self, group_collection, token_position):
        orgainsed_collection = defaultdict(list)

        for group in group_collection:
            orgainsed_collection[group['tokens'][token_position]].append(group)

        return orgainsed_collection

    def __relaxed_compare_patch_groups(self, orgainsed_collection, group_i, conservative_groups, visited_groups, relaxed_groups):
        # print(len(conservative_groups))
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

            # the first condition is to avoid repetitively merged the same group when comparing the second token
            if (not set(group_j['patch_indexes']).issubset(set(relaxed_groups[target_group_idx]['patch_indexes']))
                and len(token_diff) == 1
                and bool(set(individual_i) & set(individual_j))
                and 'revert' not in list(token_diff.keys())[0].lower()
                and not self.__is_series_intersected(series_original_id_i, series_original_id_j)
                and not self.__is_series_intersected(newseries_original_id_i, newseries_original_id_j)
                    and not self.__is_version_intersected(versions_i, versions_j)):

                # remove the merged group from the group collection being compared
                orgainsed_collection[token0_i].pop(j)

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

                group_j_idx = conservative_groups.index(group_j)
                visited_groups[group_j_idx] = target_group_idx
            else:
                j += 1

    def __relaxed_comparison(self, group_collection1, group_collection2, visited_groups, relaxed_groups, conservative_groups):

        group_collection1 = sorted(
            deepcopy(group_collection1), key=lambda x: x['tokens'])
        group_collection2 = sorted(
            deepcopy(group_collection2), key=lambda x: x['tokens'])

        # each patch is organised into a group with the same 1st/2nd token
        orgainsed_collection2_token0 = self.__organise_patch_groups_by_token(
            group_collection2, 0)
        orgainsed_collection2_token1 = self.__organise_patch_groups_by_token(
            group_collection2, 1)

        for group_i in group_collection1:
            group_i_idx = conservative_groups.index(group_i)

            if group_i_idx not in visited_groups.keys():
                relaxed_groups.append(
                    {
                        'patch_indexes': deepcopy(group_i['patch_indexes']),
                        'versions': deepcopy(group_i['versions']),
                        'bag_of_words': [deepcopy(group_i['bag_of_words'])],
                        'tokens': [deepcopy(group_i['tokens'])],
                        # 'tokens2': [tokens2_i],
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

            self.__relaxed_compare_patch_groups(
                orgainsed_collection2_token0, group_i, conservative_groups, visited_groups, relaxed_groups)

            self.__relaxed_compare_patch_groups(
                orgainsed_collection2_token1, group_i, conservative_groups, visited_groups, relaxed_groups)

    def relaxed_grouping(self, raw_data_patch):
        ecosystem = raw_data_patch[0]['original_id'].split('-')[0]

        patch_data, conservative_groups, conservative_changes = self.conservative_grouping(
            raw_data_patch)
        organised_conservative_groups = self.__organise_patch_groups_by_token_len(
            conservative_groups)

        relaxed_groups = list()
        visited_groups = dict()

        token_lengths = sorted(organised_conservative_groups.keys())

        i = 0
        while i < len(token_lengths) - 1:
            # groups with tokens length 0 will not be changed; consecutive token lengths are required
            if token_lengths[i] == 0 or token_lengths[i] + 1 != token_lengths[i + 1]:
                i += 1
                continue

            # group with token length x & group with token length x + 1
            group_collection1 = organised_conservative_groups[token_lengths[i]]
            group_collection2 = organised_conservative_groups[token_lengths[i] + 1]

            # compare these two groups
            self.__relaxed_comparison(
                group_collection1, group_collection2, visited_groups, relaxed_groups, conservative_groups)

            i += 1

        relaxed_changes = self.__create_relaxed_change(
            ecosystem, patch_data, relaxed_groups)

        return patch_data, conservative_groups, relaxed_groups, conservative_changes, relaxed_changes

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

    # Update change1 and change2 id in each comment

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

    # This function is to combine step 1 and step 2 together

    def group_patches(self, patch_data: list, comment_data: list):
        patch_data = deepcopy(patch_data)
        comment_data = deepcopy(comment_data)

        updated_patch_data, _, _, change1_data, change2_data = self.group_patches_step2(
            patch_data)

        updated_comment_data = self.update_changeid_in_comment(
            change1_data, change2_data, comment_data)

        return updated_patch_data, updated_comment_data, change1_data, change2_data

    def process_data(self, identity_data: list, series_data: list, patch_data: list, comment_data: list):

        # group identities
        individual_data = self.group_identities(identity_data)

        # update individual info in other collections
        series_data = self.update_individual_original_id(
            individual_data, series_data)
        patch_data = self.update_individual_original_id(
            individual_data, patch_data)
        comment_data = self.update_individual_original_id(
            individual_data, comment_data)

        patch_data_by_project = defaultdict(list)
        comment_data_by_project = defaultdict(list)

        for item in patch_data:
            patch_data_by_project[item['project']].append(item)

        for item in comment_data:
            comment_data_by_project[item['project']].append(item)

        newseries_data = list()
        change1_data = list()
        change2_data = list()

        updated_patch_data = list()
        updated_comment_data = list()

        for project, patch_list in patch_data_by_project.items():

            # group series
            updated_patch_list, curr_newseries_data = self.group_series(
                patch_list)
            newseries_data.extend(curr_newseries_data)

            # group patches
            comment_list = comment_data_by_project[project]
            updated_patches, updated_comments, curr_change1_data, curr_change2_data = self.group_patches(
                updated_patch_list, comment_list)

            updated_patch_data.extend(updated_patches)
            updated_comment_data.extend(updated_comments)
            change1_data.extend(curr_change1_data)
            change2_data.extend(curr_change2_data)

        return individual_data, series_data, updated_patch_data, updated_comment_data, newseries_data, change1_data, change2_data

    def __is_series_patch(self, patch_name):
        series_number = re.search('\d+/\d+', patch_name, re.IGNORECASE)
        return bool(series_number)

    # Belows are helper functions

    # def __sort_patches(self, patches):
    #     for i in range(len(patches)):
    #         patch_i = patches[i]
    #         patch_i['tokens'], patch_i['one_gram'] = self.__create_bag_of_words(
    #             patch_i['name'])

    #     return sorted(patches, key=lambda x: (x['tokens'], x['date']))

    def __extract_version_number(self, patch_name):
        patch_name = patch_name.lower()
        # [<...>,v1,<...>]
        indicator_part = re.findall(
            "^\[.*?\]\s*v\d+|\[.*?[,\s]+v\d+[,\s]+.*?\]|\[.*?[,\s]+v\d+\]|\[v\d+[,\s]+.*?\]|\(v\d+\)|\[v\d+\]|[\(\[]*patchv\d+[\)\]]*", patch_name)
        for item in indicator_part:
            indicator = re.search("v\d+", item)
            if indicator:
                version_number = re.search("\d+", indicator.group())
                return int(version_number.group())
        return -1

    def __is_version_intersected(self, list_i, list_j):
        if set(list_i) & set(list_j) == {-1}:
            return False
        return bool(set(list_i) & set(list_j))

    def __is_series_intersected(self, list_i, list_j):
        if set(list_i) & set(list_j) == {None}:
            return False
        return bool(set(list_i) & set(list_j))

    def __step1_conditions(self, token_diff, newseries_original_id_i, newseries_original_id_j, series_original_id_i, series_original_id_j) -> bool:
        return (
            len(token_diff) == 0
            and self.__is_diff_series(newseries_original_id_i, newseries_original_id_j)
            and self.__is_diff_series(series_original_id_i, series_original_id_j)
        )

    def __step2_conditions(self, individual_i, individual_j, token_diff, newseries_original_id_i, newseries_original_id_j, series_original_id_i, series_original_id_j, versions_i, versions_j):
        return (
            bool(set(individual_i) & set(individual_j))
            and len(token_diff) == 1
            and 'revert' not in list(token_diff.keys())[0].lower()
            and (not self.__is_series_intersected(newseries_original_id_i, newseries_original_id_j))
            and (not self.__is_series_intersected(series_original_id_i, series_original_id_j))
            and (not self.__is_version_intersected(versions_i, versions_j))
        )
