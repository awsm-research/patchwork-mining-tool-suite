from collections import defaultdict


class ProcessIdentity():

    def __init__(self, individual_original_id=1):
        self.individual_original_id = individual_original_id

    def organise_identity_data_by_project(self, data):
        organised_identity_data = defaultdict(list)
        occurred_identity = list()

        for item in data:
            if item not in occurred_identity:
                project_oid = item['project']
                organised_identity_data[project_oid].append(item)
                occurred_identity.append(item)

        return organised_identity_data

    def identity_grouping(self, identity_data: list, project: str):

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
