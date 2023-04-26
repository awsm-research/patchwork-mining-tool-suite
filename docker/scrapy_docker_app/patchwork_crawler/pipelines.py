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
        return 'project'
    
    elif isinstance(item, items.IdentityItem):
        return f"{item.source}_identity"

    elif isinstance(item, items.SeriesItem):
        return 'series'

    elif isinstance(item, items.PatchItem):
        return 'patch'

    elif isinstance(item, items.CommentItem):
        return 'comment'

    return type(item)

class PatchworkCrawlerPipeline:
    def process_item(self, item, spider):
        return item


class PatchworkExporterPipeline(object):

    fileNamesJson = ['project_identity', 'project', 'series_identity', 'series', 'patch_identity', 'patch', 'comment']

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
            self.files |= dict([ (name, open(f"./retrieved_data/patchwork/{spider.endpoint_type}_patchwork_{name}{spider.fileidx}.jl",'ab')) for name in self.fileNamesJson[start_idx:end_idx + 1] ])
        except FileNotFoundError:
            Path("./retrieved_data/patchwork").mkdir(parents=True, exist_ok=True)
            self.files |= dict([ (name, open(f"./retrieved_data/patchwork/{spider.endpoint_type}_patchwork_{name}{spider.fileidx}.jl",'ab')) for name in self.fileNamesJson[start_idx:end_idx + 1] ])

        # self.files = dict([ (name, f"./retrieved_data/kernel_{name}.jl") for name in self.fileNamesJson ])

        for name in self.fileNamesJson[start_idx:end_idx + 1]:
            self.exporters[name] = JsonLinesItemExporter(self.files[name])

            # identity
            if name in [self.fileNamesJson[i] for i in range (0, 5, 2)]:
                self.exporters[name].fields_to_export = [
                    'original_id',
                    'email',
                    'name',
                    'api_url',
                    'project',
                    'is_maintainer',
                ]
                self.exporters[name].start_exporting()

            # project
            if name == self.fileNamesJson[1]:
                self.exporters[name].fields_to_export = [
                    'original_id',
                    'name',
                    'repository_url',
                    'api_url',
                    'web_url',
                    'list_id',
                    'list_address',
                    'maintainer_identity',
                ]
                self.exporters[name].start_exporting()

            # series
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
                    'project',
                    'submitter_identity',
                    'submitter_individual'
                ]
                self.exporters[name].start_exporting()

            # patch
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
                    'change1',
                    'change2',
                    'mailinglist',
                    'series',
                    'newseries',
                    'submitter_identity',
                    'submitter_individual',
                    'project'
                ]
                self.exporters[name].start_exporting()

            # comment
            if name == self.fileNamesJson[6]:
                self.exporters[name].fields_to_export = [
                    'original_id',
                    'msg_id',
                    'msg_content',
                    'date',
                    'subject',
                    'reply_to_msg_id',
                    'web_url',
                    'change1',
                    'change2',
                    'mailinglist',
                    'submitter_identity',
                    'submitter_individual',
                    'patch',
                    'project'
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