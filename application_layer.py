import json, jsonlines, requests
from exceptions import InvalidFileException, InvalidItemTypeException, PostRequestException
from django.core.serializers.json import DjangoJSONEncoder
from copy import deepcopy

class DataAccess():
    
    def __init__(self, endpoint="http://localhost:8000", batch_size=100000):
        self.__item_types = ['accounts', 'projects', 'series', 'patches', 'comments']
        self.__endpoint = endpoint
        self.__base_url = self.__endpoint + "/patchwork/%s/"
        self.__batch_size = batch_size
        self.__occurred_accounts = list()


    # Input: path of the json/jsonlines file to be loaded
    # Output: a list of dictionaries
    def load_json(self, filepath):
        if filepath.lower().endswith(".json"):
            with open(f"{filepath}") as f:
                json_data = json.load(f)
                if type(json_data) == str:
                    json_data = json.loads(json_data)
            if type(json_data) != list:
                json_data = [json_data]
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
                assert set(item.keys()) == {'original_id', 'email', 'username', 'api_url', 'user_id'}

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
                    'maintainer_user_id'
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
                    'submitter_user_id'
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
                    'change_id1',
                    'change_id2',
                    'mailing_list_id',
                    'series_original_id',
                    'new_series_id',
                    'submitter_account_original_id',
                    'submitter_user_id',
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
                    'change_id1',
                    'change_id2',
                    'mailing_list_id',
                    'submitter_account_original_id',
                    'submitter_user_id',
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

                for i in range(0, len(json_data), self.__batch_size):
                    json_data_batch = json_data[i:i + self.__batch_size]
                    response = self.__post_data(json_data_batch, item_type)

                    # duplicate item (same original_id) exists -> post one by one
                    try:
                        if response.status_code == 400 and 'original_id' in [list(e.keys())[0] for e in json.loads(response.text) if e]:
                            print(f"Duplicate {item_type} exists. Start inserting one by one.")
                            for item in json_data_batch:
                                response1 = self.__post_data(item, item_type)

                                if response1.status_code != 201 and not (response1.status_code == 400 and 'original_id' in [list(e.keys())[0] for e in json.loads(response.text) if e]):
                                    raise PostRequestException(response)

                        # capture duplicate django auto id error and also others
                        elif response.status_code != 201:
                            raise PostRequestException(response)
                
                    except:
                        raise PostRequestException(response)

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
