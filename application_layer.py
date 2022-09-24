import json, jsonlines, requests
from exceptions import InvalidFileException, InvalidItemTypeException, PostRequestException
from django.core.serializers.json import DjangoJSONEncoder
from copy import deepcopy

class DataAccess():
    def __init__(self, endpoint="http://localhost:8000"):
        self.__item_types = ['accounts', 'projects', 'series', 'patches', 'comments']
        self.__endpoint = endpoint
        self.__base_url = endpoint + "/patchwork/%s"


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
    def insert_data(self, data, item_type):
        try:
            if type(data) == str:
                json_data = self.load_json(data)
            else:
                json_data = data

            if item_type not in self.__item_types:
                raise InvalidItemTypeException
            else:
                self.__validate_items(json_data, item_type)

                response = self.__post_data(json_data, item_type)

                # duplicate item (same original_id) exists
                if response.status_code == 400 and 'original_id' in json.loads(response.text).keys():
                    print(f"Duplicate {item_type} exists. Start inserting one by one.")
                    for item in json_data:
                        response1 = self.__post_data(item, item_type)

                # large item exists
                elif response.status_code == 201 and response.text != 'post completed' and json.loads(response.text):
                    large_items = json.loads(response.text)
                    for large_item in large_items:
                        response2 = self.__post_data(large_item, item_type)
                
                # capture duplicate django auto id error and also others
                elif not (response.status_code == 201 and response.text == 'post completed'):
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
            print(f"Status: {e.status_code}\nReason: {e.reason}\nText: {e.text}")


    def get_item_types(self):
        return deepcopy(self.__item_types)


    def get_endpoint(self):
        return self.__endpoint
