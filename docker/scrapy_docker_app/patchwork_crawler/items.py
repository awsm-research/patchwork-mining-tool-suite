# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PatchworkCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class MailingListItem(scrapy.Item):
    msg_id = scrapy.Field()
    subject = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    sender_name = scrapy.Field()
    web_url = scrapy.Field()
    project_original_id = scrapy.Field()
    

class AccountItem(scrapy.Item):
    original_id = scrapy.Field()
    email = scrapy.Field()
    username = scrapy.Field()
    api_url = scrapy.Field()
    user_original_id = scrapy.Field()


class ProjectAccountItem(AccountItem):
    source = 'project'


class SeriesAccountItem(AccountItem):
    source = 'series'


class PatchAccountItem(AccountItem):
    source = 'patch'


class ProjectItem(scrapy.Item):
    original_id = scrapy.Field()
    name = scrapy.Field()
    repository_url = scrapy.Field()
    api_url = scrapy.Field()
    web_url = scrapy.Field()
    list_id = scrapy.Field()
    list_address = scrapy.Field()
    maintainer_account_original_id = scrapy.Field()
    maintainer_user_original_id = scrapy.Field()


class SeriesItem(scrapy.Item):
    original_id = scrapy.Field()
    name = scrapy.Field()
    date = scrapy.Field()
    version = scrapy.Field()
    total = scrapy.Field()
    received_total = scrapy.Field()
    cover_letter_msg_id = scrapy.Field()
    cover_letter_content = scrapy.Field()
    api_url = scrapy.Field()
    web_url = scrapy.Field()
    project_original_id = scrapy.Field()
    submitter_account_original_id = scrapy.Field()
    submitter_user_original_id = scrapy.Field()


class PatchItem(scrapy.Item):
    original_id = scrapy.Field()
    name = scrapy.Field()
    state = scrapy.Field()
    date = scrapy.Field()
    msg_id = scrapy.Field()
    msg_content = scrapy.Field()
    code_diff = scrapy.Field()
    api_url = scrapy.Field()
    web_url = scrapy.Field()
    commit_ref = scrapy.Field()
    reply_to_msg_id = scrapy.Field()
    change1_original_id = scrapy.Field()
    change2_original_id = scrapy.Field()
    mailing_list_original_id = scrapy.Field()
    series_original_id = scrapy.Field()
    new_series_original_id = scrapy.Field()
    submitter_account_original_id = scrapy.Field()
    submitter_user_original_id = scrapy.Field()
    project_original_id = scrapy.Field()


class CommentItem(scrapy.Item):
    original_id = scrapy.Field()
    msg_id = scrapy.Field()
    msg_content = scrapy.Field()
    date = scrapy.Field()
    subject = scrapy.Field()
    reply_to_msg_id = scrapy.Field()
    web_url = scrapy.Field()
    change1_original_id = scrapy.Field()
    change2_original_id = scrapy.Field()
    mailing_list_original_id = scrapy.Field()
    submitter_account_original_id = scrapy.Field()
    submitter_user_original_id = scrapy.Field()
    patch_original_id = scrapy.Field()
    project_original_id = scrapy.Field()