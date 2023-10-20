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
                assert {'original_id', 'email', 'name', 'api_url',
                        'is_maintainer'}.issubset(set(item.keys()))

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

        # and not (response.status_code == 400 and 'original_id' in [list(e.keys())[0] for e in json.loads(response.text) if e]):
        if response.status_code not in [201]:
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
                    json_data = self.__filter_unique_accounts(
                        json_data, reset_account_cache)

                n_batches = len(json_data) // self.__batch_size + 1

                print(f"The data contains {len(json_data)} items.")
                print(
                    f"It will be divided into {n_batches} batches with each containing {self.__batch_size} items (or less).")
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
                            self.__post_data(
                                relation_data, "projectidentityrelation")

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
                                self.__post_data(
                                    large_content_data, item_type, 'large_content/')

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
                                self.__post_data(
                                    large_data, item_type, 'large/')
                            if large_content_data:
                                self.__post_data(
                                    large_content_data, item_type, 'large_content/')
                            if large_diff_data:
                                self.__post_data(
                                    large_diff_data, item_type, 'large_diff/')

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
                                self.__post_data(
                                    large_content_data, item_type, 'large_content/')

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
                                    identity_relation_data.append(
                                        temp_relation)

                                for individual_item in individual_info:
                                    temp_relation = {
                                        f'{change_type}_original_id': data_item['original_id'],
                                        'individual_original_id': individual_item,
                                    }
                                    individual_relation_data.append(
                                        temp_relation)

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
                                    newseries_relation_data.append(
                                        temp_relation)

                                data_item['submitter_identity'] = []
                                data_item['submitter_individual'] = []
                                data_item['series'] = []
                                data_item['newseries'] = []

                            self.__post_data(json_data_batch, item_type)
                            self.__post_data(
                                identity_relation_data, f"{change_type}identityrelation")
                            self.__post_data(
                                individual_relation_data, f"{change_type}individualrelation")
                            self.__post_data(
                                series_relation_data, f"{change_type}seriesrelation")
                            self.__post_data(
                                newseries_relation_data, f"{change_type}newseriesrelation")

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
                                    identity_relation_data.append(
                                        temp_relation)

                                for individual_item in individual_info:
                                    temp_relation = {
                                        'newseries_original_id': data_item['original_id'],
                                        'individual_original_id': individual_item,
                                    }
                                    individual_relation_data.append(
                                        temp_relation)

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
                            self.__post_data(
                                identity_relation_data, "newseriesidentityrelation")
                            self.__post_data(
                                individual_relation_data, "newseriesindividualrelation")
                            self.__post_data(
                                series_relation_data, "newseriesseriesrelation")

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
                            self.__post_data(
                                relation_data, "individualidentityrelation")

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
            print(
                f"Status: {e.response.status_code}\nReason: {e.response.reason}\nText: {e.response.text}")

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
            print(
                f"Requests status: {response.status_code}\nReason: {response.reason}\nText: {response.text}")

    def reset_occurred_accounts(self):
        self.__occurred_accounts = list()

    def get_item_types(self):
        return deepcopy(self.__item_types)

    def get_endpoint(self):
        return self.__endpoint
