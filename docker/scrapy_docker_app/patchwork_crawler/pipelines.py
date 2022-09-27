# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exporters import JsonLinesItemExporter #, JsonItemExporter
from scrapy import signals
from pydispatch import dispatcher
from pathlib import Path
from . import items


def get_item_type(item):
    # The JSON file names are used (imported) from the scrapy spider.
    if isinstance(item, items.ProjectItem):
        return 'projects'
    
    elif isinstance(item, items.AccountItem):
        return f"{item.source}_accounts"

    elif isinstance(item, items.SeriesItem):
        return 'series'

    elif isinstance(item, items.PatchItem):
        return 'patches'

    elif isinstance(item, items.CommentItem):
        return 'comments'

    return type(item)

class PatchworkCrawlerPipeline:
    def process_item(self, item, spider):
        return item


class PatchworkExporterPipeline(object):

    fileNamesJson = ['project_accounts', 'projects', 'series_accounts', 'series', 'patch_accounts', 'patches', 'comments']

    def __init__(self):
        self.files = {}
        self.exporters = {}
        dispatcher.connect(self.open_spider, signal=signals.spider_opened)
        dispatcher.connect(self.close_spider, signal=signals.spider_closed)

    def open_spider(self, spider):
        
        if spider.name == 'patchwork_project':
            start_idx = 0
            end_idx = 1

        elif spider.name == 'patchwork_series':
            start_idx = 2
            end_idx = 3

        elif spider.name == 'patchwork_patch':
            start_idx = 4
            end_idx = 6
        
        try:
            self.files |= dict([ (name, open(f"./retrieved_data/patchwork/{spider.endpoint_type}_patchwork_{name}.jl",'ab')) for name in self.fileNamesJson[start_idx:end_idx + 1] ])
        except FileNotFoundError:
            Path("./retrieved_data/patchwork").mkdir(parents=True, exist_ok=True)
            self.files |= dict([ (name, open(f"./retrieved_data/patchwork/{spider.endpoint_type}_patchwork_{name}.jl",'ab')) for name in self.fileNamesJson[start_idx:end_idx + 1] ])

        # self.files = dict([ (name, f"./retrieved_data/kernel_{name}.jl") for name in self.fileNamesJson ])

        for name in self.fileNamesJson[start_idx:end_idx + 1]:
            self.exporters[name] = JsonLinesItemExporter(self.files[name])

            if name in [self.fileNamesJson[i] for i in range (0, 5, 2)]:
                self.exporters[name].fields_to_export = [
                    'original_id',
                    'email',
                    'username',
                    'api_url',
                    'user_id'
                ]
                self.exporters[name].start_exporting()

            if name == self.fileNamesJson[1]:
                self.exporters[name].fields_to_export = [
                    'original_id',
                    'name',
                    'repository_url',
                    'api_url',
                    'web_url',
                    'list_id',
                    'list_address',
                    'maintainer_account_original_id',
                    'maintainer_user_id'
                ]
                self.exporters[name].start_exporting()

            if name == self.fileNamesJson[3]:
                self.exporters[name].fields_to_export = [
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
                ]
                self.exporters[name].start_exporting()

            if name == self.fileNamesJson[5]:
                self.exporters[name].fields_to_export = [
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
                ]
                self.exporters[name].start_exporting()

            if name == self.fileNamesJson[6]:
                self.exporters[name].fields_to_export = [
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
                ]
                self.exporters[name].start_exporting()
    

    def close_spider(self, spider):
        # for exporter in self.exporters.values():
        #     exporter.finish_exporting()
        
        # for json_file in self.files.values():
        #     json_file.close()

        if spider.name == 'patchwork_project':
            self.exporters[self.fileNamesJson[0]].finish_exporting
            self.exporters[self.fileNamesJson[1]].finish_exporting

            self.files[self.fileNamesJson[0]].close()
            self.files[self.fileNamesJson[1]].close()

        elif spider.name == 'patchwork_series':
            self.exporters[self.fileNamesJson[2]].finish_exporting
            self.exporters[self.fileNamesJson[3]].finish_exporting

            self.files[self.fileNamesJson[2]].close()
            self.files[self.fileNamesJson[3]].close()

        elif spider.name == 'patchwork_patch':
            self.exporters[self.fileNamesJson[4]].finish_exporting
            self.exporters[self.fileNamesJson[5]].finish_exporting
            self.exporters[self.fileNamesJson[6]].finish_exporting

            self.files[self.fileNamesJson[4]].close()
            self.files[self.fileNamesJson[5]].close()
            self.files[self.fileNamesJson[6]].close()


    def process_item(self, item, spider):
        item_type = get_item_type(item)
        
        if item_type in self.fileNamesJson:
            self.exporters[item_type].export_item(item)

        # return item