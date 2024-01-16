import scrapy
import json
import re
import requests
from gc import callbacks
from html.parser import HTMLParser
from scrapy.exceptions import CloseSpider
from ..items import *
from ..static.utils import PatchworkCrawlerBase

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.downloadermiddlewares.retry import get_retry_request


"""
How to run the script:
Under the package dir, run 'python -m patchwork_crawler.spiders.patchwork_api' in terminal

About static variables:
To speed up crawling, the spider will directly visit each item by their id (i.e. /api/<item type>/<id>) if possible (as the response time of visiting by page (i.e. /api/<item-type>/?page=<page num>) is quite long).
Please specify the current maximum id of series and patch.
The last item in the last page may not really have the maximum id, so the id should be added up (how many more id should be crawled is up to you).
"""
BUFFER = 20
MAX_PROJECT_ID = BUFFER + 413
MAX_SERIES_ID = BUFFER + 678657
MAX_PATCH_ID = BUFFER + 12982205

ENDPOINT_TYPE = 'kernel'


class PatchworkProjectSpider(scrapy.Spider):
    name = "patchwork_project"

    custom_settings = {
        'ITEM_PIPELINES': {'patchwork_crawler.pipelines.PatchworkExporterPipeline': 300},
        'HTTPERROR_ALLOWED_CODES': [404, 500]
    }

    def __init__(self, start_project_id=1, end_project_id=MAX_PROJECT_ID, endpoint_type=ENDPOINT_TYPE, fileidx=1, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_project_id = int(start_project_id)
        self.max_project_id = int(end_project_id)
        self.endpoint_type = endpoint_type
        self.fileidx = fileidx

        self.base_func = PatchworkCrawlerBase()

        self.start_urls = [
            f"https://patchwork.{self.endpoint_type}.org/api/projects/{self.current_project_id}"]

    def parse(self, response):
        if response.status == 200:
            # item = self.base_func.get_page_json(response)
            try:
                item = self.base_func.get_page_json(response)
            except json.decoder.JSONDecodeError as e:
                item = requests.get(response.url).json()

            maintainers = item['maintainers']
            maintainer_list = list()

            for maintainer in maintainers:
                maintainer_original_id = '-'.join(
                    [self.endpoint_type, 'user', str(maintainer['id'])])
                maintainer_api_url = maintainer['url']
                maintainer_email = maintainer['email']
                maintainer_username = maintainer['username']

                identity_item = ProjectIdentityItem(
                    original_id=maintainer_original_id,
                    email=maintainer_email,
                    name=maintainer_username,
                    api_url=maintainer_api_url,
                    project='-'.join([self.endpoint_type,
                                     'project', str(item['id'])]),
                    is_maintainer=True,
                )

                yield identity_item

                maintainer_list.append(maintainer_original_id)

            project_item = ProjectItem(
                original_id='-'.join([self.endpoint_type,
                                     'project', str(item['id'])]),
                name=item['name'],
                repository_url=item['webscm_url'],
                api_url=item['url'],
                web_url=item['web_url'],
                list_id=item['list_id'],
                list_address=item['list_email'],
                maintainer_identity=maintainer_list,
            )

            yield project_item

        elif response.status == 404:
            print(f'invalid page: {response.url}')

        elif response.status == 500:
            print(f"server error: {response.url}")

        if self.current_project_id < self.max_project_id:
            self.current_project_id += 1
            yield scrapy.Request(
                url=f"https://patchwork.{self.endpoint_type}.org/api/projects/{self.current_project_id}",
                callback=self.parse
            )


class PatchworkSeriesSpider(scrapy.Spider):

    name = "patchwork_series"

    custom_settings = {
        'ITEM_PIPELINES': {'patchwork_crawler.pipelines.PatchworkExporterPipeline': 300},
        'HTTPERROR_ALLOWED_CODES': [404, 500]
    }

    def __init__(self, start_series_id=1, end_series_id=MAX_SERIES_ID, endpoint_type=ENDPOINT_TYPE, fileidx=1, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_series_id = int(start_series_id)
        self.max_series_id = int(end_series_id)
        self.endpoint_type = endpoint_type
        self.fileidx = fileidx

        self.base_func = PatchworkCrawlerBase()

        self.start_urls = [
            f"https://patchwork.{self.endpoint_type}.org/api/series/{self.current_series_id}"]

    def parse(self, response):
        if response.status == 200:

            try:
                item = self.base_func.get_page_json(response)
            except json.decoder.JSONDecodeError as e:
                item = requests.get(response.url).json()

            submitter = item['submitter']

            series_project_original_id = '-'.join(
                [self.endpoint_type, 'project', str(item['project']['id'])])

            submitter_original_id = '-'.join(
                [self.endpoint_type, 'people', str(submitter['id'])])
            submitter_api_url = submitter['url']
            submitter_email = submitter['email']
            submitter_username = submitter['name']

            identity_item = SeriesIdentityItem(
                original_id=submitter_original_id,
                email=submitter_email,
                name=submitter_username,
                api_url=submitter_api_url,
                project=series_project_original_id,
                is_maintainer=False,
            )

            yield identity_item

            series_cover_letter_msg_id = None
            series_cover_letter_content = None
            if item['cover_letter']:
                series_cover_letter_msg_id = item['cover_letter']['msgid']
                cover_letter_url = item['cover_letter']['url']

                cover_detail = None
                while cover_detail is None:
                    cover_detail = self.base_func.get_request(cover_letter_url)
                series_cover_letter_content = cover_detail['content']

            series_item = SeriesItem(
                original_id='-'.join([self.endpoint_type,
                                     'series', str(item['id'])]),
                name=item['name'],
                date=item['date'],
                version=item['version'],
                total=item['total'],
                received_total=item['received_total'],
                cover_letter_msg_id=series_cover_letter_msg_id,
                cover_letter_content=series_cover_letter_content,
                api_url=item['url'],
                web_url=item['web_url'],
                project=series_project_original_id,
                submitter_identity=submitter_original_id,
                submitter_individual=None,
            )

            yield series_item

        elif response.status == 503:
            new_request_or_none = get_retry_request(response.request,
                                                    spider=self,
                                                    reason="empty")

            return new_request_or_none

        elif response.status == 404:
            print(f'invalid page: {response.url}')

        elif response.status == 500:
            print(f"server error: {response.url}")

        if self.current_series_id < self.max_series_id:
            self.current_series_id += 1
            yield scrapy.Request(
                url=f"https://patchwork.{self.endpoint_type}.org/api/series/{self.current_series_id}",
                callback=self.parse
            )

    def parse_cover_letter(self, response):

        try:
            item = self.base_func.get_page_json(response)
        except json.decoder.JSONDecodeError as e:
            item = requests.get(response.url).json()

        cover_letter_content = item['content']

        return cover_letter_content


class PatchworkPatchSpider(scrapy.Spider):

    name = "patchwork_patch"

    custom_settings = {
        'ITEM_PIPELINES': {'patchwork_crawler.pipelines.PatchworkExporterPipeline': 300},
        'HTTPERROR_ALLOWED_CODES': [404, 500]
    }

    def __init__(self, start_patch_id=1, end_patch_id=MAX_PATCH_ID, endpoint_type=ENDPOINT_TYPE, fileidx=1, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_patch_id = int(start_patch_id)
        self.max_patch_id = int(end_patch_id)
        self.endpoint_type = endpoint_type
        self.fileidx = fileidx

        self.base_func = PatchworkCrawlerBase()

        self.start_urls = [
            f"https://patchwork.{self.endpoint_type}.org/api/patches/{self.current_patch_id}"]

    def parse(self, response):
        if response.status == 200:

            try:
                item = self.base_func.get_page_json(response)
            except json.decoder.JSONDecodeError as e:
                item = requests.get(response.url).json()

            patch_project_original_id = '-'.join(
                [self.endpoint_type, 'project', str(item['project']['id'])])

            submitter = item['submitter']

            submitter_original_id = '-'.join(
                [self.endpoint_type, 'people', str(submitter['id'])])
            submitter_api_url = submitter['url']
            submitter_email = submitter['email']
            submitter_username = submitter['name']

            identity_item = PatchIdentityItem(
                original_id=submitter_original_id,
                email=submitter_email,
                name=submitter_username,
                api_url=submitter_api_url,
                project=patch_project_original_id,
                is_maintainer=False,
            )

            yield identity_item

            if item['series']:
                patch_series_api_id = item['series'][0]['id']
                patch_series_original_id = '-'.join(
                    [self.endpoint_type, 'series', str(patch_series_api_id)])
            else:
                patch_series_original_id = None

            patch_original_id = '-'.join([self.endpoint_type,
                                         'patch', str(item['id'])])

            patch_in_reply_to = None
            if 'In-Reply-To' in item['headers'].keys():
                patch_in_reply_to = item['headers']['In-Reply-To']

            patch_item = PatchItem(
                original_id=patch_original_id,
                name=item['name'],
                state=item['state'],
                date=item['date'],
                msg_id=item['msgid'],
                msg_content=item['content'],
                code_diff=item['diff'],
                api_url=item['url'],
                web_url=item['web_url'],
                commit_ref=item['commit_ref'],
                in_reply_to=patch_in_reply_to,
                change1=None,
                change2=None,
                mailinglist=None,
                series=patch_series_original_id,
                newseries=None,
                submitter_identity=submitter_original_id,
                submitter_individual=None,
                project=patch_project_original_id
            )

            yield patch_item

            comment_url = item['comments']
            comment_list = self.base_func.get_request(comment_url)

            if comment_list:
                for comment in comment_list:

                    comment_in_reply_to = None
                    if 'In-Reply-To' in comment['headers'].keys():
                        comment_in_reply_to = comment['headers']['In-Reply-To']
                        if comment_in_reply_to[:2] == '\n ':
                            comment_in_reply_to = comment_in_reply_to[2:]

                    comment_submitter = comment['submitter']

                    comment_submitter_original_id = '-'.join(
                        [self.endpoint_type, 'people', str(comment_submitter['id'])])
                    comment_submitter_api_url = comment_submitter['url']
                    comment_submitter_email = comment_submitter['email']
                    comment_submitter_username = comment_submitter['name']

                    comment_identity_item = PatchIdentityItem(
                        original_id=comment_submitter_original_id,
                        email=comment_submitter_email,
                        name=comment_submitter_username,
                        api_url=comment_submitter_api_url,
                        project=patch_project_original_id,
                        is_maintainer=False,
                    )

                    yield comment_identity_item

                    comment_item = CommentItem(
                        original_id='-'.join([self.endpoint_type,
                                             'comment', str(comment['id'])]),
                        msg_id=comment['msgid'],
                        msg_content=comment['content'],
                        date=comment['date'],
                        subject=comment['subject'],
                        in_reply_to=comment_in_reply_to,
                        web_url=comment['web_url'],
                        change1=None,
                        change2=None,
                        mailinglist=None,
                        submitter_identity=comment_submitter_original_id,
                        submitter_individual=None,
                        patch=patch_original_id,
                        project=patch_project_original_id
                    )

                    yield comment_item

        elif response.status == 503:
            new_request_or_none = get_retry_request(response.request,
                                                    spider=self,
                                                    reason="empty")

            return new_request_or_none

        elif response.status == 404:
            print(f'invalid page: {response.url}')

        elif response.status == 500:
            print(f"server error: {response.url}")

        if self.current_patch_id < self.max_patch_id:
            self.current_patch_id += 1
            yield scrapy.Request(
                url=f"https://patchwork.{self.endpoint_type}.org/api/patches/{self.current_patch_id}",
                callback=self.parse
            )


# if __name__ == '__main__':

#     configure_logging()
#     runner = CrawlerRunner(settings={
#         'ITEM_PIPELINES': {'patchwork_crawler.pipelines.PatchworkExporterPipeline': 300},
#         'HTTPERROR_ALLOWED_CODES': [404, 500],
#         'SPIDER_MODULES': ['patchwork_crawler.spiders'],
#         'NEWSPIDER_MODULE': 'patchwork_crawler.spiders'
#     })

#     @defer.inlineCallbacks
#     def crawl():
#         yield runner.crawl(PatchworkProjectSpider)
#         yield runner.crawl(PatchworkSeriesSpider)
#         yield runner.crawl(PatchworkPatchSpider)
#         reactor.stop()

#     crawl()
#     reactor.run()
