
from collections import defaultdict


class ProcessMailingList():

    def organise_data_by_project(self, data):
        organised_data = defaultdict(list)
        occurred_msgid = list()

        for item in data:
            if item['msg_id'] not in occurred_msgid:
                project_oid = item['project']
                organised_data[project_oid].append(item)
                occurred_msgid.append(item['msg_id'])

        return organised_data

    def organise_data(self, data):
        organised_data = list()
        occurred_msgid = list()

        for item in data:
            if item['msg_id'] not in occurred_msgid:
                organised_data.append(item)
                occurred_msgid.append(item['msg_id'])

        return organised_data
