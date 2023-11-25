import json
import requests
from tqdm import tqdm
from copy import deepcopy
from django.core.serializers.json import DjangoJSONEncoder
from application.helpers.exceptions import InvalidFileException, InvalidItemTypeException, PostRequestException
from application.helpers.constants import *

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
        self.__occurred_identities = list()
        self.__batch_size = batch_size

    # This function is to speed up the insertion of identities by removing duplicate identities in the data
    def __filter_unique_identities(self, json_data, reset_identity_cache):
        if reset_identity_cache:
            self.reset_occurred_identities()

        unique_identities = list()

        for identitiy in json_data:
            if identitiy['original_id'] not in self.__occurred_identities:
                unique_identities.append(identitiy)
                self.__occurred_identities.append(identitiy['original_id'])

        return unique_identities

    # This function is to guarantee the data to be imported to the database contain the required fields
    def __validate_items(self, json_data, item_type):

        # identity
        if item_type == self.__item_types[0]:
            for item in json_data:
                assert IDENTITY.issubset(set(item.keys()))

        # project
        elif item_type == self.__item_types[1]:
            for item in json_data:
                assert PROJECT.issubset(set(item.keys()))

        # series
        elif item_type == self.__item_types[2]:
            for item in json_data:
                assert SERIES.issubset(set(item.keys()))

        # patch
        elif item_type == self.__item_types[3]:
            for item in json_data:
                assert PATCH.issubset(set(item.keys()))

        # comment
        elif item_type == self.__item_types[4]:
            for item in json_data:
                assert COMMENT.issubset(set(item.keys()))

        # change
        elif item_type == self.__item_types[5] or item_type == self.__item_types[6]:
            for item in json_data:
                assert CHANGE.issubset(set(item.keys()))

        # new series
        elif item_type == self.__item_types[7]:
            for item in json_data:
                assert NEWSERIES.issubset(set(item.keys()))

        # mailing list
        elif item_type == self.__item_types[8]:
            for item in json_data:
                assert MAILINGLIST.issubset(set(item.keys()))

        # individual
        elif item_type == self.__item_types[9]:
            for item in json_data:
                assert INDIVIDUAL.issubset(set(item.keys()))

    # This function is to import data to the database through the Django REST API
    def __post_data(self, json_data, item_type, size_type=''):
        url = f"{self.__base_url}/{item_type}/create/{size_type}"
        payload = json.dumps(json_data, cls=DjangoJSONEncoder)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code not in [201]:
            raise PostRequestException(response)

    # This function is to preprocess data and import data to the database
    def insert_data(self, data, item_type, reset_identity_cache=False):
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
                    json_data = self.__filter_unique_identities(
                        json_data, reset_identity_cache)

                n_batches = len(json_data) // self.__batch_size + 1

                print(f"The data contains {len(json_data)} items.")
                print(
                    f"It will be divided into {n_batches} batches with each containing {self.__batch_size} items (or less).")

                for i in tqdm(range(0, n_batches * self.__batch_size, self.__batch_size)):
                    json_data_batch = json_data[i:i + self.__batch_size]

                    if json_data_batch:

                        # project
                        if item_type == self.__item_types[1]:
                            relation_data = []

                            # store many to many relation between project and identity
                            for data_item in json_data_batch:
                                maintainer_info = data_item['maintainer_identity']

                                for maintainer_item in maintainer_info:
                                    temp_relation = {
                                        'project_original_id': data_item['original_id'],
                                        'identity_original_id': maintainer_item,
                                    }
                                    relation_data.append(temp_relation)

                                data_item['maintainer_identity'] = []

                            # import project data to database
                            self.__post_data(json_data_batch, item_type)
                            # import many to many relation between project and identity to database
                            self.__post_data(
                                relation_data, "projectidentityrelation")

                        # series
                        elif item_type == self.__item_types[2]:

                            standard_data = list()
                            large_content_data = list()

                            # sort out items whose sizes exceed the limit
                            for data_item in json_data_batch:
                                if data_item['cover_letter_content'] and len(data_item['cover_letter_content']) > SIZE_LIMIT:
                                    large_content_data.append(data_item)
                                else:
                                    standard_data.append(data_item)

                            # import standard data (data within size limit) to database
                            if standard_data:
                                self.__post_data(standard_data, item_type)
                            # import large data (data exceed size limit) to database
                            if large_content_data:
                                self.__post_data(
                                    large_content_data, item_type, 'large_content/')

                        # patches
                        elif item_type == self.__item_types[3]:

                            standard_data = list()
                            large_data = list()
                            large_content_data = list()
                            large_diff_data = list()

                            # travers patch data to see if any of them contains fields exceeding size limit
                            for data_item in json_data_batch:
                                # store data with msg_content and code_diff exceed size limit in large_data
                                if (data_item['msg_content'] and len(data_item['msg_content']) > SIZE_LIMIT) and (data_item['code_diff'] and len(data_item['code_diff']) > SIZE_LIMIT):
                                    large_data.append(data_item)

                                # store data with only msg_content exceeds size limit in large_content_data
                                elif data_item['msg_content'] and len(data_item['msg_content']) > SIZE_LIMIT:
                                    large_content_data.append(data_item)

                                # store data with only code_diff exceeds size limit in large_diff_data
                                elif data_item['code_diff'] and len(data_item['code_diff']) > SIZE_LIMIT:
                                    large_diff_data.append(data_item)

                                # store data within size limit in standard_data
                                else:
                                    standard_data.append(data_item)

                            # import each type of data to database
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

                            # travers comment data to see if any of them contains fields exceeding size limit
                            for data_item in json_data_batch:
                                # store data with msg_content exceeds size limit in large_content_data
                                if data_item['msg_content'] and len(data_item['msg_content']) > SIZE_LIMIT:
                                    large_content_data.append(data_item)

                                # store data within size limit in standard_data
                                else:
                                    standard_data.append(data_item)

                            # import each type of data to database
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

                                # store many to many relation between change and identity
                                for identity_item in identity_info:
                                    temp_relation = {
                                        f'{change_type}_original_id': data_item['original_id'],
                                        'identity_original_id': identity_item,
                                    }
                                    identity_relation_data.append(
                                        temp_relation)

                                # store many to many relation between change and individual
                                for individual_item in individual_info:
                                    temp_relation = {
                                        f'{change_type}_original_id': data_item['original_id'],
                                        'individual_original_id': individual_item,
                                    }
                                    individual_relation_data.append(
                                        temp_relation)

                                # store many to many relation between change and series
                                for series_item in series_info:
                                    temp_relation = {
                                        f'{change_type}_original_id': data_item['original_id'],
                                        'series_original_id': series_item,
                                    }
                                    series_relation_data.append(temp_relation)

                                # store many to many relation between change and new series
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

                            # import change data to database
                            self.__post_data(json_data_batch, item_type)

                            # import many to many relation between change and identity to database
                            self.__post_data(
                                identity_relation_data, f"{change_type}identityrelation")

                            # import many to many relation between change and individual to database
                            self.__post_data(
                                individual_relation_data, f"{change_type}individualrelation")

                            # import many to many relation between change and series to database
                            self.__post_data(
                                series_relation_data, f"{change_type}seriesrelation")

                            # import many to many relation between change and new series to database
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

                                # store many to many relation between new series and identity
                                for identity_item in identity_info:
                                    temp_relation = {
                                        'newseries_original_id': data_item['original_id'],
                                        'identity_original_id': identity_item,
                                    }
                                    identity_relation_data.append(
                                        temp_relation)

                                # store many to many relation between new series and individual
                                for individual_item in individual_info:
                                    temp_relation = {
                                        'newseries_original_id': data_item['original_id'],
                                        'individual_original_id': individual_item,
                                    }
                                    individual_relation_data.append(
                                        temp_relation)

                                # store many to many relation between new series and series
                                for series_item in series_info:
                                    temp_relation = {
                                        'newseries_original_id': data_item['original_id'],
                                        'series_original_id': series_item,
                                    }
                                    series_relation_data.append(temp_relation)

                                data_item['submitter_identity'] = []
                                data_item['submitter_individual'] = []
                                data_item['series'] = []

                            # import new series data to database
                            self.__post_data(json_data_batch, item_type)

                            # import many to many relation between new series and identity to database
                            self.__post_data(
                                identity_relation_data, "newseriesidentityrelation")

                            # import many to many relation between new series and individual to database
                            self.__post_data(
                                individual_relation_data, "newseriesindividualrelation")

                            # import many to many relation between new series and series to database
                            self.__post_data(
                                series_relation_data, "newseriesseriesrelation")

                        # mailing list
                        elif item_type == self.__item_types[8]:

                            standard_data = list()
                            large_content_data = list()

                            # travers mailing list data to see if any of them contains fields exceeding size limit
                            for data_item in json_data_batch:

                                # store data with content exceeds size limit in large_content_data
                                if data_item['content'] and len(data_item['content']) > SIZE_LIMIT:
                                    large_content_data.append(data_item)

                                # store data within size limit in standard_data
                                else:
                                    standard_data.append(data_item)

                            # import each type of data to database
                            if standard_data:
                                self.__post_data(standard_data, item_type)
                            if large_content_data:
                                self.__post_data(
                                    large_content_data, item_type, 'large_content/')

                        # individual
                        elif item_type == self.__item_types[9]:
                            relation_data = []

                            for data_item in json_data_batch:
                                identity_info = data_item['identity']

                                # store many to many relation between individual and identity
                                for identity_item in identity_info:
                                    temp_relation = {
                                        'individual_original_id': data_item['original_id'],
                                        'identity_original_id': identity_item,
                                    }
                                    relation_data.append(temp_relation)

                                data_item['identity'] = []

                            # import individual data to database
                            self.__post_data(json_data_batch, item_type)

                            # import many to many relation between individual and identity to database
                            self.__post_data(
                                relation_data, "individualidentityrelation")

                        # others
                        else:
                            self.__post_data(json_data_batch, item_type)

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

    # This funcion is to retrieve data through Django REST API
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

    def reset_occurred_identities(self):
        self.__occurred_identities = list()

    def get_item_types(self):
        return deepcopy(self.__item_types)

    def get_endpoint(self):
        return self.__endpoint
