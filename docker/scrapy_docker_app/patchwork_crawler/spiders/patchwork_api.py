import scrapy, json, re, requests
from gc import callbacks
from html.parser import HTMLParser
from scrapy.exceptions import CloseSpider
from ..items import *
from ..static.utils import PatchworkCrawlerBase

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


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


    def __init__(self, start_project_id=1, end_project_id=MAX_PROJECT_ID, endpoint_type=ENDPOINT_TYPE, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_project_id = int(start_project_id)
        self.max_project_id = int(end_project_id)
        self.endpoint_type = endpoint_type

        self.base_func = PatchworkCrawlerBase()

        self.start_urls = [f"https://patchwork.{self.endpoint_type}.org/api/projects/{self.current_project_id}"]


    def parse(self, response):
        if response.status == 200:
            # item = self.base_func.get_page_json(response)
            try:
                item = self.base_func.get_page_json(response)
            except json.decoder.JSONDecodeError as e:
                item = requests.get(response.url).json()
            
            maintainers = item['maintainers']
            maintainer_list = list()

            # current_account_list = list()
            for maintainer in maintainers:
                maintainer_original_id = '-'.join([self.endpoint_type, 'projectaccount', str(maintainer['id'])])
                maintainer_api_url = maintainer['url']
                maintainer_email = maintainer['email']
                maintainer_username = maintainer['username']

                account_item = ProjectAccountItem(
                    original_id = maintainer_original_id,
                    email = maintainer_email,
                    username = maintainer_username,
                    api_url = maintainer_api_url,
                    user_id = None,
                )

                yield account_item

                maintainer_list.append(maintainer_original_id)
                

            project_item = ProjectItem(
                original_id = '-'.join([self.endpoint_type, 'project', str(item['id'])]),
                name = item['name'],
                repository_url = item['webscm_url'],
                api_url = item['url'],
                web_url = item['web_url'],
                list_id = item['list_id'],
                list_address = item['list_email'],
                maintainer_account_original_id = maintainer_list,
                maintainer_user_id = list()
            )

            yield project_item

        elif response.status == 404:
            print(f'invalid page: {response.url}')

        elif response.status == 500:
            print(f"server error: {response.url}")

        if self.current_project_id < self.max_project_id:
            self.current_project_id += 1
            yield scrapy.Request(
                url = f"https://patchwork.{self.endpoint_type}.org/api/projects/{self.current_project_id}",
                callback=self.parse
            )


class PatchworkSeriesSpider(scrapy.Spider):

    name = "patchwork_series"

    custom_settings = {
        'ITEM_PIPELINES': {'patchwork_crawler.pipelines.PatchworkExporterPipeline': 300},
        'HTTPERROR_ALLOWED_CODES': [404, 500]
    }

    def __init__(self, start_series_id=1, end_series_id=MAX_SERIES_ID, endpoint_type=ENDPOINT_TYPE, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_series_id = int(start_series_id)
        self.max_series_id = int(end_series_id)
        self.endpoint_type = endpoint_type

        self.base_func = PatchworkCrawlerBase()

        self.start_urls = [f"https://patchwork.{self.endpoint_type}.org/api/series/{self.current_series_id}"]

    # def start_requests(self):
    #     start_series_id = getattr(self, 'start_series_id', None)
    #     end_series_id = getattr(self, 'end_series_id', None)
    #     org = getattr(self, 'org', None)

    #     if start_series_id is not None:
    #         self.current_series_id = int(start_series_id)
    #     if end_series_id is not None:
    #         self.max_series_id = int(end_series_id)
    #     if org is not None:
    #         self.endpoint_type = endpoint_type
    #     url = f"https://patchwork.{self.endpoint_type}.org/api/series/{self.current_series_id}"
    #     yield scrapy.Request(url, self.parse)


    def parse(self, response):
        if response.status == 200:

            # get a single series json
            # item = self.base_func.get_page_json(response)
            try:
                item = self.base_func.get_page_json(response)
            except json.decoder.JSONDecodeError as e:
                item = requests.get(response.url).json()

            submitter = item['submitter']

            submitter_original_id = '-'.join([self.endpoint_type, 'account', str(submitter['id'])])
            submitter_api_url = submitter['url']
            submitter_email = submitter['email']
            submitter_username = submitter['name']


            account_item = SeriesAccountItem(
                original_id = submitter_original_id,
                email = submitter_email,
                username = submitter_username,
                api_url = submitter_api_url,
                user_id = None,
            )

            yield account_item

            series_project_original_id = '-'.join([self.endpoint_type, 'project', str(item['project']['id'])])
            
            series_cover_letter_msg_id = None
            series_cover_letter_content = None
            if item['cover_letter']:
                series_cover_letter_msg_id = item['cover_letter']['msgid']
                cover_letter_url = item['cover_letter']['url']
                
                cover_detail = self.base_func.get_request(cover_letter_url)
                series_cover_letter_content = cover_detail['content']
                

            series_item = SeriesItem(
                original_id = '-'.join([self.endpoint_type, 'series', str(item['id'])]),
                name = item['name'],
                date = item['date'],
                version = item['version'],
                total = item['total'],
                received_total = item['received_total'],
                cover_letter_msg_id = series_cover_letter_msg_id,
                cover_letter_content = series_cover_letter_content,
                api_url = item['url'],
                web_url = item['web_url'],
                project_original_id = series_project_original_id,
                submitter_account_original_id = submitter_original_id,
                submitter_user_id = None,
            )

            yield series_item
        
        elif response.status == 404:
            print(f'invalid page: {response.url}')

        elif response.status == 500:
            print(f"server error: {response.url}")
        
        
        if self.current_series_id < self.max_series_id:
            self.current_series_id += 1
            yield scrapy.Request(
                url = f"https://patchwork.{self.endpoint_type}.org/api/series/{self.current_series_id}",
                callback=self.parse
            )

    def parse_cover_letter(self, response):
        
        # item = self.base_func.get_page_json(response)
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
    

    def __init__(self, start_patch_id=1, end_patch_id=MAX_PATCH_ID, endpoint_type=ENDPOINT_TYPE, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_patch_id = int(start_patch_id)
        self.max_patch_id = int(end_patch_id)
        self.endpoint_type = endpoint_type

        self.base_func = PatchworkCrawlerBase()

        self.start_urls = [f"https://patchwork.{self.endpoint_type}.org/api/patches/{self.current_patch_id}"]


    def parse(self, response):
        if response.status == 200:

            # get a single patch json
            # item = self.base_func.get_page_json(response)
            try:
                item = self.base_func.get_page_json(response)
            except json.decoder.JSONDecodeError as e:
                item = requests.get(response.url).json()

            submitter = item['submitter']

            submitter_original_id = '-'.join([self.endpoint_type, 'account', str(submitter['id'])])
            submitter_api_url = submitter['url']
            submitter_email = submitter['email']
            submitter_username = submitter['name']


            account_item = PatchAccountItem(
                original_id = submitter_original_id,
                email = submitter_email,
                username = submitter_username,
                api_url = submitter_api_url,
                user_id = None,
            )

            yield account_item

            patch_project_original_id = '-'.join([self.endpoint_type, 'project', str(item['project']['id'])])
            
            if item['series']:
                patch_series_api_id = item['series'][0]['id']
                patch_series_original_id = '-'.join([self.endpoint_type, 'series', str(patch_series_api_id)])
            else:
                patch_series_original_id = None
            
            patch_original_id = '-'.join([self.endpoint_type, 'patch', str(item['id'])])

            patch_reply_to_msg_id = None
            if 'In-Reply-To' in item['headers'].keys():
                patch_reply_to_msg_id = item['headers']['In-Reply-To']

            patch_item = PatchItem(
                original_id = patch_original_id,
                name = item['name'],
                state = item['state'],
                date = item['date'],
                msg_id = item['msgid'],
                msg_content = item['content'],
                code_diff = item['diff'],
                api_url = item['url'],
                web_url = item['web_url'],
                commit_ref = item['commit_ref'],
                reply_to_msg_id = patch_reply_to_msg_id,
                change_id1 = None,
                change_id2 = None,
                mailing_list_id = None,
                series_original_id = patch_series_original_id,
                new_series_id = None,
                submitter_account_original_id = submitter_original_id,
                submitter_user_id = None,
                project_original_id = patch_project_original_id
            )

            yield patch_item

            comment_url = item['comments']
            comment_list = self.base_func.get_request(comment_url)
            
            if comment_list:
                for comment in comment_list:

                    comment_reply_to_msg_id = None
                    if 'In-Reply-To' in comment['headers'].keys():
                        in_reply_to = comment['headers']['In-Reply-To']
                        if in_reply_to[:2] == '\n ':
                            comment_reply_to_msg_id = in_reply_to[2:]

                    comment_submitter = comment['submitter']

                    comment_submitter_original_id = '-'.join([self.endpoint_type, 'account', str(comment_submitter['id'])])
                    comment_submitter_api_url = comment_submitter['url']
                    comment_submitter_email = comment_submitter['email']
                    comment_submitter_username = comment_submitter['name']

                    comment_account_item = PatchAccountItem(
                        original_id = comment_submitter_original_id,
                        email = comment_submitter_email,
                        username = comment_submitter_username,
                        api_url = comment_submitter_api_url,
                        user_id = None,
                    )

                    yield comment_account_item


                    comment_item = CommentItem(
                        original_id = '-'.join([self.endpoint_type, 'comment', str(comment['id'])]),
                        msg_id = comment['msgid'],
                        msg_content = comment['content'],
                        date = comment['date'],
                        subject = comment['subject'],
                        reply_to_msg_id = comment_reply_to_msg_id,
                        web_url = comment['web_url'],
                        change_id1 = None,
                        change_id2 = None,
                        mailing_list_id = None,
                        submitter_account_original_id = comment_submitter_original_id,
                        submitter_user_id = None,
                        patch_original_id = patch_original_id,
                        project_original_id = patch_project_original_id
                    )

                    yield comment_item
        
        elif response.status == 404:
            print(f'invalid page: {response.url}')

        elif response.status == 500:
            print(f"server error: {response.url}")

        
        if self.current_patch_id < self.max_patch_id:
            self.current_patch_id += 1
            yield scrapy.Request(
                url = f"https://patchwork.{self.endpoint_type}.org/api/patches/{self.current_patch_id}",
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