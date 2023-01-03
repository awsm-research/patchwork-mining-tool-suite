import json, jsonlines, requests, nltk, re, time
from exceptions import InvalidFileException, InvalidItemTypeException, PostRequestException
from django.core.serializers.json import DjangoJSONEncoder
from copy import deepcopy
from nltk.tokenize import word_tokenize
from collections import Counter, defaultdict

nltk.download('punkt', quiet=True)


class AccessData():
    
    def __init__(self, endpoint="http://localhost:8000", batch_size=100000):
        self.__item_types = [
            'accounts', 
            'projects', 
            'series', 
            'patches', 
            'comments', 
            'changes1', 
            'changes2', 
            'newseries', 
            'mailinglist',
            'users',
        ]
        self.__endpoint = endpoint
        self.__base_url = self.__endpoint + "/patchwork/%s/create/"
        self.__batch_size = batch_size
        self.__occurred_accounts = list()


    # Input: path of the json/jsonlines file to be loaded
    # Output: a list of dictionaries
    def load_json(self, filepath):
        if filepath.lower().endswith(".json"):
            with open(f"{filepath}") as f:
                json_data = json.load(f)
                json_data = json.loads(json_data) if type(json_data) == str else json_data

            json_data = [json_data] if type(json_data) != list else json_data
            return json_data

        elif filepath.lower().endswith(".jl") or filepath.lower().endswith(".jsonl"):
            with jsonlines.open(f"{filepath}") as reader:
                json_data = [obj for obj in reader]

            return json_data
        
        else:
            raise InvalidFileException()


    # This function is to speed up the insertion of accounts by removing duplicate accounts in the data
    def __filter_unique_accounts(self, json_data, reset_account_cache):
        if reset_account_cache:
            self.reset_occurred_accounts()
            
        unique_accounts = list()

        for account in json_data:
            if account['original_id'] not in self.__occurred_accounts:
                unique_accounts.append(account)
                self.__occurred_accounts.append(account['original_id'])
        
        return unique_accounts


    def __validate_items(self, json_data, item_type):
    
        # account
        if item_type == self.__item_types[0]:
            for item in json_data:
                assert set(item.keys()) == {'original_id', 'email', 'username', 'api_url', 'user_original_id'}

        # project
        elif item_type == self.__item_types[1]:
            for item in json_data:
                assert set(item.keys()) == {
                    'original_id',
                    'name',
                    'repository_url',
                    'api_url',
                    'web_url',
                    'list_id',
                    'list_address',
                    'maintainer_account_original_id',
                    'maintainer_user_original_id'
                }

        # series
        elif item_type == self.__item_types[2]:
            for item in json_data:
                assert set(item.keys()) == {
                    'original_id',
                    'name',
                    'date',
                    'version',
                    'total',
                    'received_total',
                    'cover_letter_msg_id',
                    'cover_letter_content',
                    'api_url',
                    'web_url',
                    'project_original_id',
                    'submitter_account_original_id',
                    'submitter_user_original_id'
                }

        # patch
        elif item_type == self.__item_types[3]:
            for item in json_data:
                assert set(item.keys()) == {
                    'original_id',
                    'name',
                    'state',
                    'date',
                    'msg_id',
                    'msg_content',
                    'code_diff',
                    'api_url',
                    'web_url',
                    'commit_ref',
                    'reply_to_msg_id',
                    'change1_original_id',
                    'change2_original_id',
                    'mailing_list_original_id',
                    'series_original_id',
                    'new_series_original_id',
                    'submitter_account_original_id',
                    'submitter_user_original_id',
                    'project_original_id'
                }

        # comment
        elif item_type == self.__item_types[4]:
            for item in json_data:
                assert set(item.keys()) == {
                    'original_id',
                    'msg_id',
                    'msg_content',
                    'date',
                    'subject',
                    'reply_to_msg_id',
                    'web_url',
                    'change1_original_id',
                    'change2_original_id',
                    'mailing_list_original_id',
                    'submitter_account_original_id',
                    'submitter_user_original_id',
                    'patch_original_id',
                    'project_original_id'
                }

    def __post_data(self, json_data, item_type):
        url = self.__base_url %item_type
        payload = json.dumps(json_data, cls=DjangoJSONEncoder)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload)

        return response


    # Input: data can be json objects or the file path
    def insert_data(self, data, item_type, reset_account_cache=False):
        try:
            if type(data) == str:
                json_data = self.load_json(data)
            else:
                json_data = data

            if item_type not in self.__item_types:
                raise InvalidItemTypeException
            else:
                self.__validate_items(json_data, item_type)

                if item_type == self.__item_types[0]:
                    json_data = self.__filter_unique_accounts(json_data, reset_account_cache)

                for i in range(len(json_data)):
                    # json_data_batch = json_data[i:i + self.__batch_size]
                    json_item = json_data[i]
                    response = self.__post_data(json_item, item_type)

                    if response.status_code not in [201] and not (response.status_code == 400 and 'original_id' in json.loads(response.text).keys()):
                        raise PostRequestException(response)

                    # # duplicate item (same original_id) exists -> post one by one
                    # try:
                    #     if response.status_code == 400 and 'original_id' in [list(e.keys())[0] for e in json.loads(response.text) if e]:
                    #         print(f"Duplicate {item_type} exists. Start inserting one by one.")
                    #         for item in json_data_batch:
                    #             response1 = self.__post_data(item, item_type)

                    #             if response1.status_code != 201 and not (response1.status_code == 400 and 'original_id' in [list(e.keys())[0] for e in json.loads(response.text) if e]):
                    #                 raise PostRequestException(response)

                    #     # capture duplicate django auto id error and also others
                    #     elif response.status_code != 201:
                    #         raise PostRequestException(response)
                
                    # except:
                    #     raise PostRequestException(response)

        except FileNotFoundError as e:
            print(e)
            
        except InvalidFileException as e:
            print(e)

        except InvalidItemTypeException as e:
            print(e)

        except AssertionError as e:
            print("Unexpected keys exist.")

        except PostRequestException as e:
            print(f"Status: {e.response.status_code}\nReason: {e.response.reason}\nText: {e.response.text}")


    def reset_occurred_accounts(self):
        self.__occurred_accounts = list()


    def get_all_data(self, item_type):
        url = self.__base_url %item_type
        response = requests.get(url).json()

        return response


    def get_item_types(self):
        return deepcopy(self.__item_types)


    def get_endpoint(self):
        return self.__endpoint



class ProcessInitialData():

    def __init__(self):
        pass

    def __get_distinct_accounts(self, account_data):
        new_account_data = list()
        occurred_accounts = list()
        for acc in account_data:
            if acc['original_id'] not in occurred_accounts:
                new_account_data.append(acc)
                occurred_accounts.append(acc['original_id'])

        return new_account_data

    def group_accounts(self, account_data: list):
        account_data = self.__get_distinct_accounts(account_data)
        endpoint_type = account_data[0]['original_id'].split('-')[0]
        email_dict = dict()
        username_dict = dict()
        user_dict = defaultdict(lambda: defaultdict(list))
    
        idx = 0
        
        # list for account with empty/null name/email
        username_waiting_list = list()
        email_waiting_list = list()
        
        for i in range(len(account_data)):
            account = account_data[i]
            account_email = account['email']
            account_username = account['username']
            account_orgid = account['original_id']
            
            if not account_username:
                username_waiting_list.append((i, account_orgid, account_email))
            elif not account_email:
                email_waiting_list.append((i, account_orgid, account_username))
            
            elif account_email not in email_dict.keys() and account_username not in username_dict.keys():
                user_dict[idx]['email_list'].append(account_email)
                user_dict[idx]['username_list'].append(account_username)
                user_dict[idx]['original_id_list'].append(account_orgid)
                user_dict[idx]['idx_list'].append(i)
                
                email_dict[account_email] = idx
                username_dict[account_username] = idx
                
                idx += 1
                
            elif account_email in email_dict.keys() and account_username not in username_dict.keys():
                target_idx = email_dict[account_email]
                username_dict[account_username] = target_idx
                user_dict[target_idx]['username_list'].append(account_username)
                user_dict[target_idx]['original_id_list'].append(account_orgid)
                user_dict[target_idx]['idx_list'].append(i)
                
            elif account_email not in email_dict.keys() and account_username in username_dict.keys():
                target_idx = username_dict[account_username]
                email_dict[account_email] = target_idx
                user_dict[target_idx]['email_list'].append(account_email)
                user_dict[target_idx]['original_id_list'].append(account_orgid)
                user_dict[target_idx]['idx_list'].append(i)
                
            elif account_email in email_dict.keys() and account_username in username_dict.keys() and email_dict[account_email] != username_dict[account_username]:
                email_dict_idx = email_dict[account_email]
                username_dict_idx = username_dict[account_username]
                
                email_list_to_move = user_dict[username_dict_idx]['email_list']
                username_list_to_move = user_dict[username_dict_idx]['username_list']
                orgid_list_to_move = user_dict[username_dict_idx]['original_id_list']
                idx_to_move = user_dict[username_dict_idx]['idx_list']
                
                for email in email_list_to_move:
                    email_dict[email] = email_dict_idx
                for username in username_list_to_move:
                    username_dict[username] = email_dict_idx
                    
                user_dict[email_dict_idx]['email_list'].extend(email_list_to_move)
                user_dict[email_dict_idx]['username_list'].extend(username_list_to_move)
                user_dict[email_dict_idx]['original_id_list'].extend(orgid_list_to_move)
                user_dict[email_dict_idx]['idx_list'].extend(idx_to_move)
                
                user_dict[email_dict_idx]['username_list'].append(account_username)
                user_dict[email_dict_idx]['original_id_list'].append(account_orgid)
                user_dict[email_dict_idx]['idx_list'].append(i)
                
                user_dict[username_dict_idx] = None
        
        for account_idx, orgid, email in username_waiting_list:
            if email in email_dict.keys():
                if orgid not in user_dict[email_dict[email]]['original_id_list']:
                    user_dict[email_dict[email]]['original_id_list'].append(orgid)
                    user_dict[email_dict[email]]['idx_list'].append(account_idx)
            
            else:
                email_dict[email] = idx
                user_dict[idx]['email_list'].append(email)
                user_dict[idx]['original_id_list'].append(orgid)
                user_dict[idx]['idx_list'].append(account_idx)
                
                idx += 1
        
        for account_idx, orgid, username in email_waiting_list:
            if username in username_dict.keys():
                if orgid not in user_dict[username_dict[username]]['original_id_list']:
                    user_dict[username_dict[username]]['original_id_list'].append(orgid)
                    user_dict[username_dict[username]]['idx_list'].append(account_idx)

            else:
                username_dict[username] = idx
                user_dict[idx]['username_list'].append(username)
                user_dict[idx]['original_id_list'].append(orgid)
                user_dict[idx]['idx_list'].append(account_idx)
                
                idx += 1

        user_collection = list()

        # update user id in account collection
        for _, user_info in user_dict.items():
            if user_info:
                current_user_idx = len(user_collection) + 1
                original_id_list = user_info['original_id_list']
                account_idx_list = user_info['idx_list']

                for i in account_idx_list:
                    account_data[i]['user_original_id'] = f'{endpoint_type}-user-{current_user_idx}'

                user_collection.append(
                    {
                        'original_id': f'{endpoint_type}-user-{current_user_idx}',
                        'account_original_id': original_id_list
                    }
                )
                
        return account_data, user_collection


    # This method is to update the user_id in series, newseries, patch, and comment collection
    # It should be called after the function of grouping accounts is implemented
    def update_user_original_id(self, account_data: list, collection: list, is_list=False):
        account_map = dict()
        for acc in account_data:
            account_map[acc['original_id']] = acc['user_original_id']
        

        if is_list:
            try:
                for document in collection:
                    for submitter in document['submitter_account_original_id']:
                        document['submitter_user_original_id'].append(account_map[submitter])
            except:
                for document in collection:
                    for maintainer in document['maintainer_account_original_id']:
                        document['maintainer_user_original_id'].append(account_map[maintainer])
        else:
            for document in collection:
                document['submitter_user_original_id'] = account_map[document['submitter_account_original_id']]

        # return collection


    def group_series(self, patch_data: list):
        # patch_data = deepcopy(patch_data)

        idx = 1
        series_id_map = dict()
        newseries_collection = list()
        endpoint_type = patch_data[0]['original_id'].split('-')[0]

        for patch in patch_data:
            if patch['reply_to_msg_id'] and self.__is_series_patch(patch['name']):
                reply_to_msg_id = patch['reply_to_msg_id']
                # account = patch['submitter_account_original_id']
                if type(reply_to_msg_id) == list:
                    for msg_id in reply_to_msg_id:
                        if msg_id in series_id_map.keys():
                            patch['new_series_original_id'] = f'{endpoint_type}-newseries-{series_id_map[msg_id]}'
                            for msg_id2 in reply_to_msg_id:
                                series_id_map[msg_id2] = series_id_map[msg_id]
                            break
                    
                    if not patch['new_series_original_id']:
                        patch['new_series_original_id'] = f'{endpoint_type}-newseries-{idx}'
                        newseries = {
                            'original_id': f'{endpoint_type}-newseries-{idx}',
                            'cover_letter_msg_id': reply_to_msg_id,
                            'project_original_id': patch['project_original_id'],
                            'submitter_account_original_id': [patch['submitter_account_original_id']],
                            'submitter_user_original_id': [],
                            'series_original_id': [patch['series_original_id']]
                        }
                        newseries_collection.append(newseries)

                        for msg_id in reply_to_msg_id:
                            series_id_map[msg_id] = idx
                        
                        idx += 1
                    else:
                        newseries_collection[series_id_map[reply_to_msg_id[0]] - 1]['cover_letter_msg_id'].extend(reply_to_msg_id)
                        if patch['submitter_account_original_id'] not in newseries_collection[series_id_map[reply_to_msg_id[0]] - 1]['submitter_account_original_id']:
                            newseries_collection[series_id_map[reply_to_msg_id[0]] - 1]['submitter_account_original_id'].append(patch['submitter_account_original_id'])
                        if patch['series_original_id'] not in newseries_collection[series_id_map[reply_to_msg_id[0]] - 1]['series_original_id']:
                            newseries_collection[series_id_map[reply_to_msg_id[0]] - 1]['series_original_id'].append(patch['series_original_id'])

                    # for msg_id in reply_to_msg_id:
                    #     series_id_map[msg_id] = patch['new_series_original_id']

                else:
                    if reply_to_msg_id in series_id_map.keys():
                        patch['new_series_original_id'] = f'{endpoint_type}-newseries-{series_id_map[reply_to_msg_id]}'
                        if patch['submitter_account_original_id'] not in newseries_collection[series_id_map[reply_to_msg_id] - 1]['submitter_account_original_id']:
                            newseries_collection[series_id_map[reply_to_msg_id] - 1]['submitter_account_original_id'].append(patch['submitter_account_original_id'])
                        if patch['series_original_id'] not in newseries_collection[series_id_map[reply_to_msg_id] - 1]['series_original_id']:
                            newseries_collection[series_id_map[reply_to_msg_id] - 1]['series_original_id'].append(patch['series_original_id'])
                    else:
                        patch['new_series_original_id'] = idx
                        series_id_map[reply_to_msg_id] = idx

                        newseries = {
                            'original_id': f'{endpoint_type}-newseries-{idx}',
                            'cover_letter_msg_id': [reply_to_msg_id],
                            'project_original_id': patch['project_original_id'],
                            'submitter_account_original_id': [patch['submitter_account_original_id']],
                            'submitter_user_original_id': [],
                            'series_original_id': [patch['series_original_id']]
                        }
                        newseries_collection.append(newseries)

                        idx += 1
                
        for s in newseries_collection:
            s['inspection_needed'] = True if len(s['cover_letter_msg_id']) > 1 else False

        return newseries_collection


    # This function is to group patches based on the criteria in step 1
    # It should be called after newseries collection is created 
    def group_patches_step1(self, patch_data):
        endpoint_type = patch_data[0]['original_id'].split('-')[0]
        sorted_patch_data = self.__sort_patches(patch_data)

        # patches of the same review process will be saved in the same group in the list
        step1_groups = list()
        # each visited patch is saved with the index number of the group in patch_groups
        visited_patches = dict()

        i = 0
        while i < len(sorted_patch_data):
            patch_i = sorted_patch_data[i]
            if patch_i['code_diff'] == None or patch_i['code_diff'] == '':
                i += 1
                continue

            one_gram_i = patch_i['one_gram']
            original_id_i = patch_i['original_id']
            name_i = patch_i['name']
            submitter_i = patch_i['submitter_account_original_id']
            user_i = patch_i['submitter_user_original_id']
            tokens_i = sorted(patch_i['tokens'])
            series_original_id_i = patch_i['series_original_id']
            new_series_original_id_i = patch_i['new_series_original_id']
            state_i = patch_i['state']
            commit_id_i = patch_i['commit_ref']

            # version will be -1 if there is no version indicator in patch name
            version_i = self.__extract_version_number(name_i)

            step1_groups.append(
                {
                    'group': [i], 
                    'versions': [version_i],
                    'one_gram': one_gram_i,
                    'tokens': tokens_i,
                    'tokens2': tokens_i[1:],
                    'state': [state_i],
                    'commit_id': [commit_id_i],
                    'project_original_id': patch_i['project_original_id'],
                    'submitters': [submitter_i],
                    'users': [user_i],
                    'series_original_ids': [series_original_id_i],
                    'new_series_original_ids': [new_series_original_id_i],
                }
            )
            visited_patches[original_id_i] = len(step1_groups) - 1

            j = i + 1
            while j < len(sorted_patch_data):
                patch_j = sorted_patch_data[j]
                
                one_gram_j = patch_j['one_gram']
                original_id_j = patch_j['original_id']
                name_j = patch_j['name']
                submitter_j = patch_j['submitter_account_original_id']
                user_j = patch_j['submitter_user_original_id']
                tokens_j = sorted(patch_j['tokens'])
                series_original_id_j = patch_j['series_original_id']
                new_series_original_id_j = patch_j['new_series_original_id']
                version_j = self.__extract_version_number(name_j)
                state_j = patch_j['state']
                commit_id_j = patch_j['commit_ref']
                
                token_diff = (one_gram_i | one_gram_j) - (one_gram_i & one_gram_j)


                if self.__step1_conditions(token_diff, new_series_original_id_i, new_series_original_id_j, series_original_id_i, series_original_id_j):
                    target_group_idx = visited_patches[original_id_i]
                    step1_groups[target_group_idx]['group'].append(j)
                    step1_groups[target_group_idx]['versions'].append(version_j)
                    step1_groups[target_group_idx]['submitters'].append(submitter_j)
                    step1_groups[target_group_idx]['users'].append(user_j)
                    step1_groups[target_group_idx]['series_original_ids'].append(series_original_id_j)
                    step1_groups[target_group_idx]['new_series_original_ids'].append(new_series_original_id_j)
                    step1_groups[target_group_idx]['state'].append(state_j)
                    step1_groups[target_group_idx]['commit_id'].append(commit_id_j)

                    # patch_j['change1_original_id'] = target_group_idx

                    j += 1

                else:
                    break

            i = j

        change1_collection = list()
        for j in range(len(step1_groups)):
            group = step1_groups[j]

            is_accepted = True if 'accepted' in group['state'] else False
            commit_ids = list(set(group['commit_id']))
            if None in commit_ids:
                commit_ids.remove(None)
            merged_commit_id = commit_ids if commit_ids else None
            project_original_id = group['project_original_id']
            submitter_account_original_id = list(set(group['submitters']))
            submitter_user_original_id = list(set(group['users']))
            series_original_id = list(set(group['series_original_ids']))
            new_series_original_id = list(set(group['new_series_original_ids']))

            tmp_dict = {
                'original_id': f'{endpoint_type}-change1-{j + 1}',
                'is_accepted': is_accepted,
                'parent_commit_id': None,
                'merged_commit_id': merged_commit_id,
                'commit_date': None,
                'project_original_id': project_original_id,
                'submitter_account_original_id': submitter_account_original_id,
                'submitter_user_original_id': submitter_user_original_id,
                'series_original_id': series_original_id,
                'new_series_original_id': new_series_original_id,
                'patch_original_id': [sorted_patch_data[i]['original_id'] for i in group['group']],
                'inspection_needed': False,
            }

            for patch_idx in group['group']:
                if sorted_patch_data[patch_idx]['change1_original_id'] == None:
                    sorted_patch_data[patch_idx]['change1_original_id'] = f'{endpoint_type}-change1-{j + 1}'
                else:
                    tmp_dict['inspection_needed'] = True

                    group_idx = int(sorted_patch_data[patch_idx]['change1_original_id'].split('-')[-1]) - 1
                    change1_collection[group_idx]['inspection_needed'] = True


            change1_collection.append(tmp_dict)

        return sorted_patch_data, step1_groups, change1_collection

    
    def group_patches_step2(self, patch_data):
        endpoint_type = patch_data[0]['original_id'].split('-')[0]

        sorted_patch_data, step1_groups, change1_collection = self.group_patches_step1(patch_data)
        group_data = self.__sort_groups(step1_groups)

        step2_groups = list()
        visited_groups = dict()

        token_lengths = sorted(group_data.keys())

        for curr_len in token_lengths:
            curr_groups = group_data[curr_len]
            next_groups = deepcopy(group_data[curr_len + 1]) if (curr_len + 1) in token_lengths else list()

            # traverse curr_group
            st = time.time()
            for group_i in curr_groups:
                if curr_groups.index(group_i) % 200 == 0:
                    et = time.time()
                    print(f"token_length {curr_len} - group {curr_groups.index(group_i)} - time: {(et - st) / 60: .2f} min")
                    st = time.time()

                group_i_idx = step1_groups.index(group_i)
                versions_i = deepcopy(group_i['versions'])
                one_gram_i = group_i['one_gram']
                tokens_i = group_i['tokens']
                tokens2_i = group_i['tokens2']
                submitter_i = group_i['submitters']
                user_i = group_i['users']
                series_original_id_i = group_i['series_original_ids']
                new_series_original_id_i = group_i['new_series_original_ids']

                if group_i_idx not in visited_groups.keys():
                    step2_groups.append(
                        {
                            'group': group_i['group'],
                            'versions': versions_i,
                            'one_gram': [one_gram_i],
                            'tokens': [tokens_i],
                            'tokens2': [tokens2_i],
                            'series_original_ids': series_original_id_i,
                            'new_series_original_ids': new_series_original_id_i,
                            
                            'state': group_i['state'],
                            'commit_id': group_i['commit_id'],
                            'project_original_id': group_i['project_original_id'],
                            'submitters': submitter_i,
                            'users': user_i,
                        }
                    )
                    visited_groups[group_i_idx] = len(step2_groups) - 1

                    # for patch_idx in group_i['group']:
                    #     patch_data[patch_idx]['change2_original_id'] = visited_groups[group_i_idx]

                if next_groups:
                    next_groups = sorted(next_groups, key = lambda x: x['tokens'])

                    # rationale: if diff == 1, at least one of the first two 
                    # tokens in group_j is the same as the 1st token in group_i 
                    # (token length of group_i is 1 less than that of group_j)

                    # match group_i 1st token with group_j 1st token
                    j = 0
                    while j < len(next_groups):
                        group_j = next_groups[j]
                        # print('group_i:', group_i)
                        # print('group_j:', group_j)
                        if group_i['tokens'] and group_j['tokens']:
                            if group_i['tokens'][0] < group_j['tokens'][0]:
                                break
                            if group_i['tokens'][0] == group_j['tokens'][0]:
                                group_j_idx = step1_groups.index(group_j)
                                versions_j = deepcopy(group_j['versions'])
                                one_gram_j = group_j['one_gram']
                                tokens_j = group_j['tokens']
                                submitter_j = group_j['submitters']
                                user_j = group_j['users']
                                series_original_id_j = group_j['series_original_ids']
                                new_series_original_id_j = group_j['new_series_original_ids']

                                token_diff = (one_gram_i | one_gram_j) - (one_gram_i & one_gram_j)

                                if self.__step2_conditions(user_i, user_j, token_diff, new_series_original_id_i, new_series_original_id_j, series_original_id_i, series_original_id_j, versions_i, versions_j):
                                    next_groups.pop(j)

                                    target_idx = visited_groups[group_i_idx]
                                    step2_groups[target_idx]['group'].extend(group_j['group'])
                                    step2_groups[target_idx]['versions'].extend(versions_j)
                                    step2_groups[target_idx]['series_original_ids'].extend(series_original_id_j)
                                    step2_groups[target_idx]['new_series_original_ids'].extend(new_series_original_id_j)
                                    step2_groups[target_idx]['one_gram'].append(one_gram_j)
                                    step2_groups[target_idx]['tokens'].append(tokens_j)

                                    step2_groups[target_idx]['state'].extend(group_j['state'])
                                    step2_groups[target_idx]['commit_id'].extend(group_j['commit_id'])
                                    step2_groups[target_idx]['submitters'].extend(group_j['submitters'])
                                    step2_groups[target_idx]['users'].extend(group_j['users'])

                                    visited_groups[group_j_idx] = target_idx

                                    # for patch_idx in group_j['group']:
                                    #     patch_data[patch_idx]['change2_original_id'] = target_idx
                                else:
                                    j += 1

                            else:
                                j += 1

                        else:
                            j += 1

                    # match group_i 1st token with group_j 2nd token
                    next_groups = sorted(next_groups, key = lambda x: x['tokens2'])
                    if len(group_i['tokens']) > 1 and next_groups:
                        j = 0
                        while j < len(next_groups):
                            group_j = next_groups[j]
                            if group_i['tokens'] and group_j['tokens']:
                                if group_i['tokens'][1] < group_j['tokens2'][0]:
                                    break
                                if group_i['tokens'][1] == group_j['tokens2'][0]:
                                    group_j_idx = step1_groups.index(group_j)
                                    versions_j = deepcopy(group_j['versions'])
                                    one_gram_j = group_j['one_gram']
                                    tokens_j = group_j['tokens']
                                    submitter_j = group_j['submitters']
                                    series_original_id_j = group_j['series_original_ids']
                                    new_series_original_id_j = group_j['new_series_original_ids']

                                    token_diff = (one_gram_i | one_gram_j) - (one_gram_i & one_gram_j)

                                    if self.__step2_conditions(user_i, user_j, token_diff, new_series_original_id_i, new_series_original_id_j, series_original_id_i, series_original_id_j, versions_i, versions_j):
                                        next_groups.pop(j)

                                        target_idx = visited_groups[group_i_idx]
                                        step2_groups[target_idx]['group'].extend(group_j['group'])
                                        step2_groups[target_idx]['versions'].extend(versions_j)
                                        step2_groups[target_idx]['series_original_ids'].extend(series_original_id_j)
                                        step2_groups[target_idx]['new_series_original_ids'].extend(new_series_original_id_j)
                                        step2_groups[target_idx]['one_gram'].append(one_gram_j)
                                        step2_groups[target_idx]['tokens'].append(tokens_j)

                                        step2_groups[target_idx]['state'].extend(group_j['state'])
                                        step2_groups[target_idx]['commit_id'].extend(group_j['commit_id'])
                                        step2_groups[target_idx]['submitters'].extend(group_j['submitters'])
                                        step2_groups[target_idx]['users'].extend(group_j['users'])

                                        visited_groups[group_j_idx] = target_idx

                                        # for patch_idx in group_j['group']:
                                        #     patch_data[patch_idx]['change2_original_id'] = target_idx
                                    else:
                                        j += 1
                                else:
                                    j += 1
                            else:
                                j += 1
                else:
                    break

        change2_collection = list()
        for j in range(len(step2_groups)):
            group = step2_groups[j]
            is_accepted = True if 'accepted' in group['state'] else False
            commit_ids = list(set(group['commit_id']))
            if None in commit_ids:
                commit_ids.remove(None)
            merged_commit_id = commit_ids if commit_ids else None
            project_original_id = group['project_original_id']
            submitter_account_original_id = list(set(group['submitters']))
            submitter_user_original_id = list(set(group['users']))
            series_original_id = list(set(group['series_original_ids']))
            new_series_original_id = list(set(group['new_series_original_ids']))

            tmp_dict = {
                'original_id': f'{endpoint_type}-change2-{j + 1}',
                'is_accepted': is_accepted,
                'parent_commit_id': None,
                'merged_commit_id': merged_commit_id,
                'commit_date': None,
                'project_original_id': project_original_id,
                'submitter_account_original_id': submitter_account_original_id,
                'submitter_user_original_id': submitter_user_original_id,
                'series_original_id': series_original_id,
                'new_series_original_id': new_series_original_id,
                'patch_original_id': [sorted_patch_data[i]['original_id'] for i in group['group']],
                'inspection_needed': False,
            }

            for patch_idx in group['group']:
                if sorted_patch_data[patch_idx]['change2_original_id'] == None:
                    sorted_patch_data[patch_idx]['change2_original_id'] = f'{endpoint_type}-change2-{j + 1}'
                else:
                    tmp_dict['inspection_needed'] = True

                    group_idx = int(sorted_patch_data[patch_idx]['change2_original_id'].split('-')[-1]) - 1
                    change2_collection[group_idx]['inspection_needed'] = True

            change2_collection.append(tmp_dict)

        return sorted_patch_data, step1_groups, step2_groups, change1_collection, change2_collection


    def __is_series_patch(self, patch_name):
        series_number = re.search('\d+/\d+', patch_name, re.IGNORECASE)
        return bool(series_number)
                    

    def __create_one_gram(self, patch_name):
        patch_name = patch_name.lower()

        # case 1: [<header>]v1<main title>
        if re.findall("^\[.*?\]\s*v\d+.+", patch_name):
            # replace the content in the first bracket
            patch_name = re.sub(r'\[.*?\]\s*v\d+', ' ', patch_name, 1)
            
        # case 2: [<header>]<main title>
        elif re.findall("^\[.*?\].+", patch_name):
            patch_name = re.sub(r'\[.*?\]', ' ', patch_name, 1) # replace the content in the first bracket
        
        # replace patchv1, <series number>, [v1], (v1), <punctuations>
        patch_words = re.sub(r'[\(\[]patch[\)\]]|\[*patchv\d+\]*|\d+/\d+\W|\[v\d+\]|\(v\d+\)|[^\w\s/-]', ' ', patch_name)
        tokens = word_tokenize(patch_words)
        one_gram = Counter(tokens)
            
        return tokens, one_gram


    def __sort_patches(self, patches):
        for i in range(len(patches)):
            patch_i = patches[i]
            patch_i['tokens'], patch_i['one_gram'] = self.__create_one_gram(patch_i['name'])
        
        return sorted(patches, key=lambda x: (x['tokens'], x['date']))


    def __sort_groups(self, groups):
        sorted_groups = defaultdict(list)
        for i in range(len(groups)):
            group_i = groups[i]
            group_token_length = len(group_i['tokens'])
            sorted_groups[group_token_length].append(deepcopy(group_i))
        return sorted_groups


    def __extract_version_number(self, patch_name):
        patch_name = patch_name.lower()
        # [<...>,v1,<...>]
        indicator_part = re.findall("^\[.*?\]\s*v\d+|\[.*?[,\s]+v\d+[,\s]+.*?\]|\[.*?[,\s]+v\d+\]|\[v\d+[,\s]+.*?\]|\(v\d+\)|\[v\d+\]|[\(\[]*patchv\d+[\)\]]*", patch_name)
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


    def __is_diff_series(self, series_id1, series_id2):
        if series_id1 is None and series_id2 is None:
            return True

        return series_id1 != series_id2


    def __is_series_intersected(self, list_i, list_j):
        if set(list_i) & set(list_j) == {None}:
            return False
        return bool(set(list_i) & set(list_j))


    def __step1_conditions(self, token_diff, new_series_original_id_i, new_series_original_id_j, series_original_id_i, series_original_id_j) -> bool:
        return (
            len(token_diff) == 0
            and self.__is_diff_series(new_series_original_id_i, new_series_original_id_j)
            and self.__is_diff_series(series_original_id_i, series_original_id_j)
        )


    def __step2_conditions(self, user_i, user_j, token_diff, new_series_original_id_i, new_series_original_id_j, series_original_id_i, series_original_id_j, versions_i, versions_j):
        return (
            bool(set(user_i) & set(user_j))
            and len(token_diff) == 1
            and 'revert' not in list(token_diff.keys())[0].lower()
            and (not self.__is_series_intersected(new_series_original_id_i, new_series_original_id_j))
            and (not self.__is_series_intersected(series_original_id_i, series_original_id_j))
            and (not self.__is_version_intersected(versions_i, versions_j))
        )