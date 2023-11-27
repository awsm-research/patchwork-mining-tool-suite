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
    original_id = scrapy.Field()
    msg_id = scrapy.Field()
    subject = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    sender_name = scrapy.Field()
    web_url = scrapy.Field()
    project = scrapy.Field()


class IdentityItem(scrapy.Item):
    original_id = scrapy.Field()
    email = scrapy.Field()
    name = scrapy.Field()
    api_url = scrapy.Field()
    project = scrapy.Field()
    is_maintainer = scrapy.Field()


class ProjectIdentityItem(IdentityItem):
    source = 'project'


class SeriesIdentityItem(IdentityItem):
    source = 'series'


class PatchIdentityItem(IdentityItem):
    source = 'patch'


class ProjectItem(scrapy.Item):
    original_id = scrapy.Field()
    name = scrapy.Field()
    repository_url = scrapy.Field()
    api_url = scrapy.Field()
    web_url = scrapy.Field()
    list_id = scrapy.Field()
    list_address = scrapy.Field()
    maintainer_identity = scrapy.Field()


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
    project = scrapy.Field()
    submitter_identity = scrapy.Field()
    submitter_individual = scrapy.Field()


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
    in_reply_to = scrapy.Field()
    change1 = scrapy.Field()
    change2 = scrapy.Field()
    mailinglist = scrapy.Field()
    series = scrapy.Field()
    newseries = scrapy.Field()
    submitter_identity = scrapy.Field()
    submitter_individual = scrapy.Field()
    project = scrapy.Field()


class CommentItem(scrapy.Item):
    original_id = scrapy.Field()
    msg_id = scrapy.Field()
    msg_content = scrapy.Field()
    date = scrapy.Field()
    subject = scrapy.Field()
    in_reply_to = scrapy.Field()
    web_url = scrapy.Field()
    change1 = scrapy.Field()
    change2 = scrapy.Field()
    mailinglist = scrapy.Field()
    submitter_identity = scrapy.Field()
    submitter_individual = scrapy.Field()
    patch = scrapy.Field()
    project = scrapy.Field()
