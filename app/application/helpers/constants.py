IDENTITY = {'original_id', 'email', 'name', 'api_url', 'is_maintainer'}

PROJECT = {
    'original_id',
    'name',
    'repository_url',
    'api_url',
    'web_url',
    'list_id',
    'list_address',
    'maintainer_identity'
}

SERIES = {
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
}

PATCH = {
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
}

COMMENT = {
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
}

CHANGE = {
    'original_id',
    'is_accepted',
    'parent_commit_id',
    'merged_commit_id',
    'commit_date',
    'project',
    'inspection_needed'
}

NEWSERIES = {
    'original_id',
    'cover_letter_msg_id',
    'project',
    'submitter_identity',
    'submitter_individual',
    'series',
    'inspection_needed'
}

MAILINGLIST = {
    'original_id',
    'msg_id',
    'subject',
    'content',
    'date',
    'sender_name',
    'web_url',
    'project'
}

INDIVIDUAL = {
    'original_id',
    'project',
    'identity'
}
