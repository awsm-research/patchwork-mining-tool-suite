import json, jsonlines, requests, nltk, re, time, pymongo
from exceptions import InvalidFileException, InvalidItemTypeException, PostRequestException
from django.core.serializers.json import DjangoJSONEncoder
from copy import deepcopy
from nltk.tokenize import word_tokenize
from collections import Counter, defaultdict
from tqdm import tqdm

nltk.download('punkt', quiet=True)

SIZE_LIMIT = 16793600

class AccessData():
    
    def __init__(self, endpoint="http://localhost:8000", batch_size=10000):
        self.__item_types = [
            'identity', 
            'project', 
            'series', 
            'patch', 
            'comment', 
            'change1', 
            'change2', 
            'newseries', 
            'mailinglist',
            'individual',
        ]
        self.__endpoint = endpoint
        self.__base_url = self.__endpoint + "/patchwork"
        self.__occurred_accounts = list()
        self.__batch_size = batch_size


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


    # This function is to guarantee the data to be posted contain the required fields
    def __validate_items(self, json_data, item_type):
    
        # identity
        if item_type == self.__item_types[0]:
            for item in json_data:
                assert {'original_id', 'email', 'name', 'api_url', 'is_maintainer'}.issubset(set(item.keys()))

        # project
        elif item_type == self.__item_types[1]:
            for item in json_data:
                assert {
                    'original_id',
                    'name',
                    'repository_url',
                    'api_url',
                    'web_url',
                    'list_id',
                    'list_address',
                    'maintainer_identity',
                    # 'maintainer_individual'
                }.issubset(set(item.keys()))

        # series
        elif item_type == self.__item_types[2]:
            for item in json_data:
                assert {
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
                    'project',
                    'submitter_identity',
                    'submitter_individual'
                }.issubset(set(item.keys()))

        # patch
        elif item_type == self.__item_types[3]:
            for item in json_data:
                assert {
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
                    'in_reply_to',
                    'change1',
                    'change2',
                    'mailinglist',
                    'series',
                    'newseries',
                    'submitter_identity',
                    'submitter_individual',
                    'project'
                }.issubset(set(item.keys()))

        # comment
        elif item_type == self.__item_types[4]:
            for item in json_data:
                assert {
                    'original_id',
                    'msg_id',
                    'msg_content',
                    'date',
                    'subject',
                    'in_reply_to',
                    'web_url',
                    'change1',
                    'change2',
                    'mailinglist',
                    'submitter_identity',
                    'submitter_individual',
                    'patch',
                    'project'
                }.issubset(set(item.keys()))

        # change
        elif item_type == self.__item_types[5] or item_type == self.__item_types[6]:
            for item in json_data:
                assert {
                    'original_id',
                    'is_accepted',
                    'parent_commit_id',
                    'merged_commit_id',
                    'commit_date',
                    'project',
                    # 'submitter_identity',
                    # 'submitter_individual',
                    # 'series',
                    # 'newseries',
                    'inspection_needed'
                }.issubset(set(item.keys()))
        
        # newseries
        elif item_type == self.__item_types[7]:
            for item in json_data:
                assert {
                    'original_id',
                    'cover_letter_msg_id',
                    'project',
                    'submitter_identity',
                    'submitter_individual',
                    'series',
                    'inspection_needed'
                }.issubset(set(item.keys()))
        
        # mailing list
        elif item_type == self.__item_types[8]:
            for item in json_data:
                assert {
                    'original_id',
                    'msg_id',
                    'subject',
                    'content',
                    'date'
                    'sender_name',
                    'web_url',
                    'project'
                }.issubset(set(item.keys()))

        
        # individual
        elif item_type == self.__item_types[9]:
            for item in json_data:
                assert {
                    'original_id',
                    'project',
                    'identity'
                }.issubset(set(item.keys()))



    # This function is to post data through the Django REST API
    def __post_data(self, json_data, item_type, size_type=''):
        url = f"{self.__base_url}/{item_type}/create/{size_type}"
        payload = json.dumps(json_data, cls=DjangoJSONEncoder)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code not in [201]: # and not (response.status_code == 400 and 'original_id' in [list(e.keys())[0] for e in json.loads(response.text) if e]):
            raise PostRequestException(response)
        
        # return response


    # Input: data can be json objects or the file path
    def insert_data(self, data, item_type, reset_account_cache=False):
        try:
            if type(data) == str:
                json_data = self.load_json(data)
            elif type(data) == dict:
                json_data = [data]
            else:
                json_data = data

            if item_type not in self.__item_types:
                raise InvalidItemTypeException
            else:
                self.__validate_items(json_data, item_type)

                if item_type == self.__item_types[0]:
                    json_data = self.__filter_unique_accounts(json_data, reset_account_cache)

                n_batches = len(json_data) // self.__batch_size + 1

                print(f"The data contains {len(json_data)} items.")
                print(f"It will be divided into {n_batches} batches with each containing {self.__batch_size} items (or less).")
                # print(f"It will take around 1.5 minutes to insert one batch.")

                for i in tqdm(range(0, n_batches * self.__batch_size, self.__batch_size)):
                    json_data_batch = json_data[i:i + self.__batch_size]

                    if json_data_batch:
                        # print(f"Start to insert batch {int(i / self.__batch_size + 1)}")
                        # st = time.time()

                        # project
                        if item_type == self.__item_types[1]:
                            relation_data = []

                            for data_item in json_data_batch:
                                maintainer_info = data_item['maintainer_identity']

                                for maintainer_item in maintainer_info:
                                    temp_relation = {
                                        'project_original_id': data_item['original_id'],
                                        'identity_original_id': maintainer_item,
                                    }
                                    relation_data.append(temp_relation)
                                
                                data_item['maintainer_identity'] = []

                            self.__post_data(json_data_batch, item_type)
                            self.__post_data(relation_data, "projectidentityrelation")

                        # series
                        elif item_type == self.__item_types[2]:

                            standard_data = list()
                            large_content_data = list()

                            for data_item in json_data_batch:
                                if data_item['cover_letter_content'] and len(data_item['cover_letter_content']) > SIZE_LIMIT:
                                    large_content_data.append(data_item)
                                else:
                                    standard_data.append(data_item)

                            if standard_data:
                                self.__post_data(standard_data, item_type)
                            if large_content_data:
                                self.__post_data(large_content_data, item_type, 'large_content/')

                        # patches
                        elif item_type == self.__item_types[3]:
                        
                            standard_data = list()
                            large_data = list()
                            large_content_data = list()
                            large_diff_data = list()

                            for data_item in json_data_batch:
                                if (data_item['msg_content'] and len(data_item['msg_content']) > SIZE_LIMIT) and (data_item['code_diff'] and len(data_item['code_diff']) > SIZE_LIMIT):
                                    large_data.append(data_item)
                                elif data_item['msg_content'] and len(data_item['msg_content']) > SIZE_LIMIT:
                                    large_content_data.append(data_item)
                                elif data_item['code_diff'] and len(data_item['code_diff']) > SIZE_LIMIT:
                                    large_diff_data.append(data_item)
                                else:
                                    standard_data.append(data_item)

                            if standard_data:
                                self.__post_data(standard_data, item_type)
                            if large_data:
                                self.__post_data(large_data, item_type, 'large/')
                            if large_content_data:
                                self.__post_data(large_content_data, item_type, 'large_content/')
                            if large_diff_data:
                                self.__post_data(large_diff_data, item_type, 'large_diff/')

                        # comments
                        elif item_type == self.__item_types[4]:
                        
                            standard_data = list()
                            large_content_data = list()

                            for data_item in json_data_batch:
                                if data_item['msg_content'] and len(data_item['msg_content']) > SIZE_LIMIT:
                                    large_content_data.append(data_item)
                                else:
                                    standard_data.append(data_item)

                            if standard_data:
                                self.__post_data(standard_data, item_type)
                            if large_content_data:
                                self.__post_data(large_content_data, item_type, 'large_content/')
                        
                        # change
                        elif item_type == self.__item_types[5] or item_type == self.__item_types[6]:
                            change_type = 'change1' if item_type == self.__item_types[5] else 'change2'

                            identity_relation_data = []
                            individual_relation_data = []
                            series_relation_data = []
                            newseries_relation_data = []

                            for data_item in json_data_batch:
                                identity_info = data_item['submitter_identity']
                                individual_info = data_item['submitter_individual']
                                series_info = data_item['series']
                                newseries_info = data_item['newseries']

                                for identity_item in identity_info:
                                    temp_relation = {
                                        f'{change_type}_original_id': data_item['original_id'],
                                        'identity_original_id': identity_item,
                                    }
                                    identity_relation_data.append(temp_relation)

                                for individual_item in individual_info:
                                    temp_relation = {
                                        f'{change_type}_original_id': data_item['original_id'],
                                        'individual_original_id': individual_item,
                                    }
                                    individual_relation_data.append(temp_relation)

                                for series_item in series_info:
                                    temp_relation = {
                                        f'{change_type}_original_id': data_item['original_id'],
                                        'series_original_id': series_item,
                                    }
                                    series_relation_data.append(temp_relation)

                                for newseries_item in newseries_info:
                                    temp_relation = {
                                        f'{change_type}_original_id': data_item['original_id'],
                                        'newseries_original_id': newseries_item,
                                    }
                                    newseries_relation_data.append(temp_relation)
                                
                                data_item['submitter_identity'] = []
                                data_item['submitter_individual'] = []
                                data_item['series'] = []
                                data_item['newseries'] = []

                            self.__post_data(json_data_batch, item_type)
                            self.__post_data(identity_relation_data, f"{change_type}identityrelation")
                            self.__post_data(individual_relation_data, f"{change_type}individualrelation")
                            self.__post_data(series_relation_data, f"{change_type}seriesrelation")
                            self.__post_data(newseries_relation_data, f"{change_type}newseriesrelation")

                        
                        # newseries
                        elif item_type == self.__item_types[7]:
                            identity_relation_data = []
                            individual_relation_data = []
                            series_relation_data = []

                            for data_item in json_data_batch:
                                identity_info = data_item['submitter_identity']
                                individual_info = data_item['submitter_individual']
                                series_info = data_item['series']

                                for identity_item in identity_info:
                                    temp_relation = {
                                        'newseries_original_id': data_item['original_id'],
                                        'identity_original_id': identity_item,
                                    }
                                    identity_relation_data.append(temp_relation)

                                for individual_item in individual_info:
                                    temp_relation = {
                                        'newseries_original_id': data_item['original_id'],
                                        'individual_original_id': individual_item,
                                    }
                                    individual_relation_data.append(temp_relation)

                                for series_item in series_info:
                                    temp_relation = {
                                        'newseries_original_id': data_item['original_id'],
                                        'series_original_id': series_item,
                                    }
                                    series_relation_data.append(temp_relation)
                                
                                data_item['submitter_identity'] = []
                                data_item['submitter_individual'] = []
                                data_item['series'] = []

                            self.__post_data(json_data_batch, item_type)
                            self.__post_data(identity_relation_data, "newseriesidentityrelation")
                            self.__post_data(individual_relation_data, "newseriesindividualrelation")
                            self.__post_data(series_relation_data, "newseriesseriesrelation")

                        # individual
                        elif item_type == self.__item_types[9]:
                            relation_data = []

                            for data_item in json_data_batch:
                                identity_info = data_item['identity']

                                for identity_item in identity_info:
                                    temp_relation = {
                                        'individual_original_id': data_item['original_id'],
                                        'identity_original_id': identity_item,
                                    }
                                    relation_data.append(temp_relation)
                                
                                data_item['identity'] = []

                            self.__post_data(json_data_batch, item_type)
                            self.__post_data(relation_data, "individualidentityrelation")

                        # others
                        else:
                            self.__post_data(json_data_batch, item_type)

                        # et = time.time()
                        # print(f"Insertion of batch {i / self.__batch_size + 1} is completed in {(et - st) / 60: .2f} minutes.")

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


    # This funcion is to retrieve data through REST API
    def retrieve_data(self, item_type, filter=''):
        filter = f"?{filter}" if filter else ''
        url = f"{self.__base_url}/{item_type}/{filter}"

        try:
            response = requests.get(url)
            retrieved_data = response.json()
            return retrieved_data
        except json.JSONDecodeError:
            print("Invalid filters.")
            print(f"Requests status: {response.status_code}\nReason: {response.reason}\nText: {response.text}")


    def reset_occurred_accounts(self):
        self.__occurred_accounts = list()


    def get_item_types(self):
        return deepcopy(self.__item_types)


    def get_endpoint(self):
        return self.__endpoint



class ProcessInitialData():

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
                identity_with_empty_name.append((i, identity_orgid, identity_email))
            elif not identity_email:
                identity_with_empty_email.append((i, identity_orgid, identity_name))
            
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
                individual_dict[target_idx]['original_id_list'].append(identity_orgid)
                
            elif identity_email not in email_dict.keys() and identity_name in name_dict.keys():
                target_idx = name_dict[identity_name]
                email_dict[identity_email] = target_idx
                individual_dict[target_idx]['email_list'].append(identity_email)
                individual_dict[target_idx]['original_id_list'].append(identity_orgid)
                
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
                        
                    individual_dict[email_dict_idx]['email_list'].extend(email_list_to_move)
                    individual_dict[email_dict_idx]['name_list'].extend(name_list_to_move)
                    individual_dict[email_dict_idx]['original_id_list'].extend(orgid_list_to_move)
                    
                    individual_dict[email_dict_idx]['name_list'].append(identity_name)
                    individual_dict[email_dict_idx]['original_id_list'].append(identity_orgid)
                    
                    individual_dict[name_dict_idx] = None
                else:
                    target_idx = email_dict[identity_email]
                    individual_dict[target_idx]['original_id_list'].append(identity_orgid)
        
        for identity_idx, orgid, email in identity_with_empty_name:
            if email in email_dict.keys():
                if orgid not in individual_dict[email_dict[email]]['original_id_list']:
                    individual_dict[email_dict[email]]['original_id_list'].append(orgid)
            
            else:
                email_dict[email] = idx
                individual_dict[idx]['email_list'].append(email)
                individual_dict[idx]['original_id_list'].append(orgid)
                
                idx += 1
        
        for identity_idx, orgid, name in identity_with_empty_email:
            if name in name_dict.keys():
                if orgid not in individual_dict[name_dict[name]]['original_id_list']:
                    individual_dict[name_dict[name]]['original_id_list'].append(orgid)

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
        identity_data_by_project = self.__get_distinct_identities(identity_data)

        individual_data = list()

        for project, identity_list in identity_data_by_project.items():
            curr_individual_data = self.__group_identities_by_project(identity_list, project)

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
                    document['submitter_individual'].append(identity_individual_map[document['project']][submitter])
            else:
                document['submitter_individual'] = identity_individual_map[document['project']][document['submitter_identity']]
        
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

                        newseries_collection[current_original_id]['cover_letter_msg_id'].extend(in_reply_to)
                        
                        if patch['submitter_identity'] not in newseries_collection[current_original_id]['submitter_identity']:
                            newseries_collection[current_original_id]['submitter_identity'].append(patch['submitter_identity'])

                        if patch['submitter_individual'] and patch['submitter_individual'] not in newseries_collection[current_original_id]['submitter_individual']:
                            newseries_collection[current_original_id]['submitter_individual'].append(patch['submitter_individual'])

                        if patch['series'] and patch['series'] not in newseries_collection[current_original_id]['series']:
                            newseries_collection[current_original_id]['series'].append(patch['series'])

                else:

                    if in_reply_to in msgid_newseries_map.keys():
                        current_original_id = f'{ecosystem}-newseries-{msgid_newseries_map[in_reply_to]}'

                        patch['newseries'] = current_original_id
                        if patch['submitter_identity'] not in newseries_collection[current_original_id]['submitter_identity']:
                            newseries_collection[current_original_id]['submitter_identity'].append(patch['submitter_identity'])
                        
                        if patch['submitter_individual'] and patch['submitter_individual'] not in newseries_collection[current_original_id]['submitter_individual']:
                            newseries_collection[current_original_id]['submitter_individual'].append(patch['submitter_individual'])

                        if patch['series'] and patch['series'] not in newseries_collection[current_original_id]['series']:
                            newseries_collection[current_original_id]['series'].append(patch['series'])
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
            s['inspection_needed'] = True if len(s['cover_letter_msg_id']) > 1 else False
            if len(s['cover_letter_msg_id']) == 1:
                s['cover_letter_msg_id'] = s['cover_letter_msg_id'][0]

        return patch_data, newseries_data


    # This function is to group patches based on the criteria in step 1
    # It should be called after newseries collection is created 
    def group_patches_step1(self, patch_data):
        ecosystem = patch_data[0]['original_id'].split('-')[0]
        sorted_patch_data = self.__sort_patches(patch_data)

        # patches of the same review process will be saved in the same group in the list
        step1_groups = list()
        # each visited patch is saved with the index number of the group in patch_groups
        visited_patches = dict()

        i = 0
        while i < len(sorted_patch_data):
            patch_i = sorted_patch_data[i]
            if not patch_i['code_diff']:
                i += 1
                continue

            one_gram_i = patch_i['one_gram']
            original_id_i = patch_i['original_id']
            name_i = patch_i['name']
            submitter_i = patch_i['submitter_identity']
            individual_i = patch_i['submitter_individual']
            tokens_i = sorted(patch_i['tokens'])
            series_original_id_i = patch_i['series']
            newseries_original_id_i = patch_i['newseries']
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
                    'project': patch_i['project'],
                    'submitters': [submitter_i],
                    'individuals': [individual_i],
                    'series_original_ids': [series_original_id_i],
                    'newseries_original_ids': [newseries_original_id_i],
                }
            )
            visited_patches[original_id_i] = len(step1_groups) - 1

            if len(tokens_i) == 0:
                i += 1
                continue

            j = i + 1
            while j < len(sorted_patch_data):
                patch_j = sorted_patch_data[j]

                if not patch_j['code_diff']:
                    j += 1
                    continue
                
                one_gram_j = patch_j['one_gram']
                name_j = patch_j['name']
                submitter_j = patch_j['submitter_identity']
                individual_j = patch_j['submitter_individual']
                series_original_id_j = patch_j['series']
                newseries_original_id_j = patch_j['newseries']
                version_j = self.__extract_version_number(name_j)
                state_j = patch_j['state']
                commit_id_j = patch_j['commit_ref']
                
                token_diff = (one_gram_i | one_gram_j) - (one_gram_i & one_gram_j)


                if self.__step1_conditions(token_diff, newseries_original_id_i, newseries_original_id_j, series_original_id_i, series_original_id_j):
                    target_group_idx = visited_patches[original_id_i]
                    step1_groups[target_group_idx]['group'].append(j)
                    step1_groups[target_group_idx]['versions'].append(version_j)
                    step1_groups[target_group_idx]['submitters'].append(submitter_j)
                    step1_groups[target_group_idx]['individuals'].append(individual_j)
                    step1_groups[target_group_idx]['series_original_ids'].append(series_original_id_j)
                    step1_groups[target_group_idx]['newseries_original_ids'].append(newseries_original_id_j)
                    step1_groups[target_group_idx]['state'].append(state_j)
                    step1_groups[target_group_idx]['commit_id'].append(commit_id_j)

                    j += 1

                else:
                    break

            i = j

        change1_collection = list()
        tmp_id_map = dict()
        for j in range(len(step1_groups)):
            group = step1_groups[j]

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
                'patch': [sorted_patch_data[i]['original_id'] for i in group['group']],
                'inspection_needed': inspection_needed,
            }

            tmp_id_map[f'{ecosystem}-change1-{self.change1_original_id}'] = j

            for patch_idx in group['group']:
                if sorted_patch_data[patch_idx]['change1'] == None:
                    sorted_patch_data[patch_idx]['change1'] = f'{ecosystem}-change1-{self.change1_original_id}'
                else:
                    # label current change1 as inspection needed
                    tmp_dict['inspection_needed'] = True

                    # track the conflicting change1 and label it inpection needed
                    group_idx = tmp_id_map[sorted_patch_data[patch_idx]['change1']]
                    change1_collection[group_idx]['inspection_needed'] = True


            change1_collection.append(tmp_dict)
            self.change1_original_id += 1

        return sorted_patch_data, step1_groups, change1_collection

    
    def group_patches_step2(self, patch_data: list):
        base_st = time.time()

        ecosystem = patch_data[0]['original_id'].split('-')[0]

        sorted_patch_data, step1_groups, change1_collection = self.group_patches_step1(patch_data)
        group_data = self.__sort_groups(step1_groups)

        print('*************************************************************')

        print('step2 started')
        for k, v in sorted(group_data.items(), key=lambda x: x[0]):
            print(f'token length: {k} -> number of groups: {len(v)}')

        print('*************************************************************')

        step2_groups = list()
        visited_groups = dict()

        token_lengths = sorted(group_data.keys())

        for curr_len in token_lengths:
            curr_groups = group_data[curr_len]
            next_groups = deepcopy(group_data[curr_len + 1]) if (curr_len + 1) in token_lengths else list()

            # traverse curr_group
            st = time.time()
            for group_i in curr_groups:
                if curr_groups.index(group_i) % 500 == 0:
                    et = time.time()
                    print(f"token_length {curr_len} - group {curr_groups.index(group_i)} - time: {(et - st) / 60: .2f} min, total: {(et - base_st) / 60: .2f} min")
                    st = time.time()

                group_i_idx = step1_groups.index(group_i)
                versions_i = deepcopy(group_i['versions'])
                one_gram_i = group_i['one_gram']
                tokens_i = group_i['tokens']
                tokens2_i = group_i['tokens2']
                submitter_i = group_i['submitters']
                individual_i = group_i['individuals']
                series_original_id_i = group_i['series_original_ids']
                newseries_original_id_i = group_i['newseries_original_ids']

                if group_i_idx not in visited_groups.keys():
                    step2_groups.append(
                        {
                            'group': group_i['group'],
                            'versions': versions_i,
                            'one_gram': [one_gram_i],
                            'tokens': [tokens_i],
                            'tokens2': [tokens2_i],
                            'series_original_ids': series_original_id_i,
                            'newseries_original_ids': newseries_original_id_i,
                            
                            'state': group_i['state'],
                            'commit_id': group_i['commit_id'],
                            'project': group_i['project'],
                            'submitters': submitter_i,
                            'individuals': individual_i,
                        }
                    )
                    visited_groups[group_i_idx] = len(step2_groups) - 1

                if next_groups and curr_len > 0:
                    next_groups = sorted(next_groups, key = lambda x: x['tokens'])

                    # rationale: if diff == 1, at least one of the first two 
                    # tokens in group_j is the same as the 1st token in group_i 
                    # (token length of group_i is 1 less than that of group_j)

                    # match group_i 1st token with group_j 1st token
                    j = 0
                    while j < len(next_groups):
                        group_j = next_groups[j]
                        
                        if group_i['tokens'][0] < group_j['tokens'][0]:
                            break
                        if group_i['tokens'][0] == group_j['tokens'][0]:
                            group_j_idx = step1_groups.index(group_j)
                            versions_j = deepcopy(group_j['versions'])
                            one_gram_j = group_j['one_gram']
                            tokens_j = group_j['tokens']
                            individual_j = group_j['individuals']
                            series_original_id_j = group_j['series_original_ids']
                            newseries_original_id_j = group_j['newseries_original_ids']

                            token_diff = (one_gram_i | one_gram_j) - (one_gram_i & one_gram_j)

                            if self.__step2_conditions(individual_i, individual_j, token_diff, newseries_original_id_i, newseries_original_id_j, series_original_id_i, series_original_id_j, versions_i, versions_j):
                                next_groups.pop(j)

                                target_idx = visited_groups[group_i_idx]
                                step2_groups[target_idx]['group'].extend(group_j['group'])
                                step2_groups[target_idx]['versions'].extend(versions_j)
                                step2_groups[target_idx]['series_original_ids'].extend(series_original_id_j)
                                step2_groups[target_idx]['newseries_original_ids'].extend(newseries_original_id_j)
                                step2_groups[target_idx]['one_gram'].append(one_gram_j)
                                step2_groups[target_idx]['tokens'].append(tokens_j)

                                step2_groups[target_idx]['state'].extend(group_j['state'])
                                step2_groups[target_idx]['commit_id'].extend(group_j['commit_id'])
                                step2_groups[target_idx]['submitters'].extend(group_j['submitters'])
                                step2_groups[target_idx]['individuals'].extend(group_j['individuals'])

                                visited_groups[group_j_idx] = target_idx

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
                            
                            if group_i['tokens'][1] < group_j['tokens2'][0]:
                                break
                            if group_i['tokens'][1] == group_j['tokens2'][0]:
                                group_j_idx = step1_groups.index(group_j)
                                versions_j = deepcopy(group_j['versions'])
                                one_gram_j = group_j['one_gram']
                                tokens_j = group_j['tokens']
                                individual_j = group_j['individuals']
                                series_original_id_j = group_j['series_original_ids']
                                newseries_original_id_j = group_j['newseries_original_ids']

                                token_diff = (one_gram_i | one_gram_j) - (one_gram_i & one_gram_j)

                                if self.__step2_conditions(individual_i, individual_j, token_diff, newseries_original_id_i, newseries_original_id_j, series_original_id_i, series_original_id_j, versions_i, versions_j):
                                    next_groups.pop(j)

                                    target_idx = visited_groups[group_i_idx]
                                    step2_groups[target_idx]['group'].extend(group_j['group'])
                                    step2_groups[target_idx]['versions'].extend(versions_j)
                                    step2_groups[target_idx]['series_original_ids'].extend(series_original_id_j)
                                    step2_groups[target_idx]['newseries_original_ids'].extend(newseries_original_id_j)
                                    step2_groups[target_idx]['one_gram'].append(one_gram_j)
                                    step2_groups[target_idx]['tokens'].append(tokens_j)

                                    step2_groups[target_idx]['state'].extend(group_j['state'])
                                    step2_groups[target_idx]['commit_id'].extend(group_j['commit_id'])
                                    step2_groups[target_idx]['submitters'].extend(group_j['submitters'])
                                    step2_groups[target_idx]['individuals'].extend(group_j['individuals'])

                                    visited_groups[group_j_idx] = target_idx

                                else:
                                    j += 1
                            else:
                                j += 1

        change2_collection = list()
        tmp_id_map = dict()

        for j in range(len(step2_groups)):
            group = step2_groups[j]
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
                'patch': [sorted_patch_data[i]['original_id'] for i in group['group']],
                'inspection_needed': inspection_needed,
            }

            tmp_id_map[current_original_id] = j

            for patch_idx in group['group']:
                if sorted_patch_data[patch_idx]['change2'] == None:
                    sorted_patch_data[patch_idx]['change2'] = current_original_id
                else:
                    tmp_dict['inspection_needed'] = True

                    group_idx = tmp_id_map[sorted_patch_data[patch_idx]['change2']]
                    change2_collection[group_idx]['inspection_needed'] = True

            change2_collection.append(tmp_dict)
            self.change2_original_id += 1

        return sorted_patch_data, step1_groups, step2_groups, change1_collection, change2_collection


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

        updated_patch_data, _, _, change1_data, change2_data = self.group_patches_step2(patch_data)

        updated_comment_data = self.update_changeid_in_comment(change1_data, change2_data, comment_data)

        return updated_patch_data, updated_comment_data, change1_data, change2_data
    

    def process_data(self, identity_data: list, series_data: list, patch_data: list,comment_data: list):

        # group identities
        individual_data = self.group_identities(identity_data)

        # update individual info in other collections
        series_data = self.update_individual_original_id(individual_data, series_data)
        patch_data = self.update_individual_original_id(individual_data, patch_data)
        comment_data = self.update_individual_original_id(individual_data, comment_data)

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
            updated_patch_list, curr_newseries_data = self.group_series(patch_list)
            newseries_data.extend(curr_newseries_data)

            # group patches
            comment_list = comment_data_by_project[project]
            updated_patches, updated_comments, curr_change1_data, curr_change2_data = self.group_patches(updated_patch_list, comment_list)

            updated_patch_data.extend(updated_patches)
            updated_comment_data.extend(updated_comments)
            change1_data.extend(curr_change1_data)
            change2_data.extend(curr_change2_data)


        return individual_data, series_data, updated_patch_data, updated_comment_data, newseries_data, change1_data, change2_data


    def __is_series_patch(self, patch_name):
        series_number = re.search('\d+/\d+', patch_name, re.IGNORECASE)
        return bool(series_number)
                    

    # Belows are helper functions
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