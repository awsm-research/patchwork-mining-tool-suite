# Code-Review-Mining

_abstract_
<!-- TODO add abstract -->

## Introduction

This project provides a suite of tools for mining and further processing Patchwork data. It consists of three parts:
- Scrapy framework for crawling data
- Django REST framework and Python application for accessing and processing the data
- MongoDB database for storing the data

## Table of Content
1. [Provided dataset](#1-provided-dataset)
    1. [Get provided dataset](#11-get-provided-dataset)
    2. [Analyse provided dataset](#12-analyse-provided-dataset)
2. [Data crawling](#2-data-crawling)
    1. [Basic steps for crawling](#21-basic-steps-for-crawling)
        1. [Schedule spiders on scrapyd](#211-schedule-spiders-on-scrapyd)
        2. [Run spiders from script](#212-run-spiders-from-script)
        3. [Run spiders using commands](#213-run-spiders-using-commands)
    2. [Customise spiders](#22-customise-spiders)
        1. [Customise spiders in scrapyd](#221-customise-spiders-in-scrapyd)
        2. [Customise spiders from script](#222-customise-spiders-from-script)
        3. [Customise spiders run using commands](#223-customise-spiders-run-using-commands)
3. [Data dictionary](#3-data-dictionary)
    1. [Application filter](#31-application-filter)


## 1. Provided dataset
The provided dataset contains data of all sub-projects in [FFmpeg](https://patchwork.ffmpeg.org/project/ffmpeg/list/), [Ozlabs](http://patchwork.ozlabs.org), and [Kernel](https://patchwork.kernel.org) until 30/09/2022. There are ten collections in which Projects, Accounts, Series, Patches, and Comments store the original crawled data (some fields will be updated during further processing), and Users, Changes1, Changes2, NewSeries, and MailingLists record the results of processing. 

### 1.1. Get provided dataset
The compressed complete dataset can be downloaded from [link](TODO). Decompress the downloaded file in root folder of the project to use in the folowing step.

### 1.2. Use provided dataset
To use the provided dataset, simply run docker containers without migrating database by using following commands in the terminal. 
```command
cd docker

# build docker images
docker-compose -f docker-compose-non-migrate.yml build 

# run docker containers
docker-compose -f docker-compose-non-migrate.yml up -d
```

Then, restore the database by running following command.
```command
docker exec -i mongodb_docker_container sh -c 'exec mongorestore --archive --nsInclude=code_review_db.*' < /path/to/code_review_db.archive
```

After restoration process is done, Mongodb database will be available for local access at `mongodb://localhost:27017`. 

#### 1.2.1. Access database directly
The sample analyses on code review metrics in a Jupyter [notebook](./analysis/review-analysis.ipynb) and their outputs can be found in folder analysis.

#### 1.2.2. Access database via Python application

Data stored in the MongoDB database can be retrieved through Django REST API by simply using the `retrieve_data` method in the Python application either as the whole set of data in a collection or as a specific set by using the filters.

##### Retrieve the whole collection

The item type of the data to be retrieved has to be specified. Available item types include *projects, accounts, series, patches, comments, newseries, changes1, changes2, mailinglists, and users*.

```python
from application_layer import AccessData

access_data = AccessData()
item_type = 'projects'
retrieved_data = access_data.retrieve_data(item_type)
```

##### Retrieve a specific set of data
Similarly, the item type also needs to be specified. To filter data, specify the filter in the arguments.

```python
from application_layer import AccessData

access_data = AccessData()
item_type = 'series'

# filter series data which belong to the FFmpeg project and whose cover letter message content contains the word "improve"
filter = 'project_original_id=ffmpeg-project-1&cover_letter_content_contain=improve'
retrieved_data = access_data.retrieve_data(item_type, filter)
```

All available filters can be found in section [Application filter](#31-application-filter).

## 2. Data crawling
To crawl new data from the source, apply the Scrapy framework in the suite. Retrieved data will be firt stored in jsonlines files. The file content can be inserted into the database with the help of the application layer. 

There are three spiders for crawling patchwork data. Their **spider names** are **patchwork_project**, **patchwork_series**, and **patchwork_patch**.
- *patchwork_project crawls patchwork projects and corresponding maintainer accounts data.*
- *patchwork_series crawls patchwork series and corresponding series submitter accounts data.*
- *patchwork_patch crawls patchwork patches, comments and corresponding submitter accounts data.*

The retrieved data will be stored under `/docker/scrapy_docker_app/retrieved_data`.

### 2.1. Basic steps for crawling
There are three ways to run spiders.
* Schedule spiders on scrapyd
* Run spiders from a script
* Run spiders using commands.

#### 2.1.1. Schedule spiders on scrapyd
Run the docker containers by entering following commands in terminal. 
```command
cd docker

# build docker images
docker-compose -f docker-compose.yml build 

# run docker containers
docker-compose -f docker-compose.yml up -d
```

Then, run the following command to schedule and run a spider in scapyd. Multiple spiders can be run and manage by scrapyd.
```command
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name>
```

#### 2.1.2. Run spiders from script

A basic structure for running from the script is provided in `/docker/scrapy_docker_app/patchwork_crawler/spiders/patchwork_api.py`.

```python
if __name__ == '__main__':

    configure_logging()
    runner = CrawlerRunner(settings={
        'ITEM_PIPELINES': {'patchwork_crawler.pipelines.PatchworkExporterPipeline': 300},
        'HTTPERROR_ALLOWED_CODES': [404, 500],
        'SPIDER_MODULES': ['patchwork_crawler.spiders'],
        'NEWSPIDER_MODULE': 'patchwork_crawler.spiders'
    })

    @defer.inlineCallbacksx
    def crawl():
        yield runner.crawl(PatchworkProjectSpider)
        yield runner.crawl(PatchworkSeriesSpider)
        yield runner.crawl(PatchworkPatchSpider)
        reactor.stop()

    crawl()
    reactor.run()
```

To run the spider, run the following command under `/scrapy_docker_app/patchwork_crawler` in the **container terminal**.

```command
python -m patchwork_crawler.spiders.patchwork_api
```

For more information, visit the [scrapy documentation](https://docs.scrapy.org/en/latest/topics/practices.html)

#### 2.1.3. Run spiders using commands

Run the following command in the **container terminal**.
```command
scrapy crawl <spider-name>
```

### 2.2. Customise spiders

Each spider crawls patchwork api web page by item id (e.g. patch id -> `https://patchwork.ffmpeg.org/api/patches/1/`). It automatically increases the item id to crawl the next web page until the id number reaches the default limit or the specified limit. The start id and the endpoint to be crawled can be specified, if necessary.


#### 2.2.1. Customise spiders in scrapyd

Pass arguments in the command. **Each argument should follow an option `-d`.**

```command
# crawl projects
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name> -d start_project_id=<specified-id> -d end_project_id=<specified-id> -d endpoint_type=<endpoint-name>

# crawl series
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name> -d start_series_id=<specified-id> -d end_series_id=<specified-id> -d endpoint_type =<endpoint-name>

# crawl patches
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name> -d start_patch_id=<specified-id> -d end_patch_id=<specified-id> -d endpoint_type =<endpoint-name>
```

#### 2.2.2. Customise spiders from script

In the provided structure, specify the argument in the crawlers.

```python
@defer.inlineCallbacks
    def crawl():
        yield runner.crawl(PatchworkProjectSpider, start_project_id=..., end_project_id=..., endpoint_type=...)
        yield runner.crawl(PatchworkSeriesSpider, start_series_id=..., end_series_id=..., endpoint_type=...)
        yield runner.crawl(PatchworkPatchSpider, start_patch_id=..., end_patch_id=..., endpoint_type=...)
        reactor.stop()
```

#### 2.2.3. Customise spiders run using commands

Similar to customisation in scrapyd, with the argument option `-a`
```command
# take crawling project as an example
scrapy crawl <spider-name> -a start_project_id=<specified-id> -a end_project_id=<specified-id> -a endpoint_type=<endpoint-name>
```
## 3. Data dictionary
<!-- TODO add high-level ER diagram -->
This section describes the high-level structure of the dataset.
### Collections
- [Accounts](#Accounts)
- [Users](#Users)
- [Projects](#Projects)
- [Series](#Series)
- [Patches](#Patches)
- [Comments](#Comments)
- [NewSeries](#NewSeries)
- [Changes1/Changes2](#Changes1Changes2)
- [MailingLists](#MailingLists)


#### Accounts

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of endpoint type, item type, and original Django id presented in the api data, e.g. `ffmpeg-account-1`; Note that for maintainer accounts of a project, the item type will become `projectaccount`, e.g. `FFmpeg-projectaccount-1` |
| email       | Email of the account |
| username    | Name of the account  |
| api_url     | API URL for retrieving the original data in patchwork (Authentication needed as patchwork blocks the access) |
| user_original_id | Referencing the original id in user collection; Accounts with the same user original id are considered as the same person |

#### Users

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of endpoint type, item type, and an auto-generated index, e.g. `ffmpeg-user-1` |
| account_original_id | An array of `original_id` of all accounts which belong to the same person |


#### Projects

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of endpoint type, item type, and original Django id presented in the api data, e.g. `ffmpeg-project-1` |
| name        | Name of the project |
| repository_url | URL of the git repository of the project if applicable |
| api_url     | API URL for retrieving the project data in patchwork |
| web_url     | URL of the project web page (if applicable) |
| list_id     | Id of the mailing list of the project |
| list_address | Email address of the mailing list of the project |
| maintainer_account_original_id | An array of ids referencing the `original_id` in the accounts collection |
| maintainer_user_original_id | An array of ids referencing the `original_id ` in the users collection |


#### Series

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of endpoint type, item type, and original Django id presented in the api data, e.g. `ffmpeg-series-1` |
| name        | Name of the series (maybe null) |
| date        | Created date of the series      |
| version     | Version of the series           |
| total       | Number of patches submitted under the series |
| received_total | Number of patches submitted under the series and received by the mailing list |
| cover_letter_msg_id | Message id of the cover letter email (the email that all following patch emails reply to) |
| cover_letter_content | Content of the cover letter email (maybe null) |
| api_url | API URL for retrieving the series data in patchwork |
| web_url | URL of the series in patchwork |
| project_original_id | Referencing the `original_id` in the projects collection |
| submitter_account_original_id | Referencing the `original_id` in the accounts collection |
| submitter_user_original_id | Referencing the `original_id ` in the users collection |


#### Patches

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto increment id generated by Django |
| original_id | A combination of endpoint type, item type, and original Django id presented in the api data, e.g. `ffmpeg-patch-1` |
| name        | Name of the patch |
| state       | Status of the patch (accepted, superseded, new, etc.) |
| date        | Date when the patch is submitted |
| msg_id      | Message id of the patch, which can be referenced to message id of the original email in the mailing list |
| msg_content | Message content of the patch |
| code_diff   | Differences of the code changes in the patch |
| api_url     | API URL for retrieving the patch data in patchwork |
| web_url     | URL of the patch in patchwork |
| commit_ref  | Commit id in the corresponding git repository |
| reply_to_msg_id | Message id of the email that the patch replies to (in most cases, it is the msg_id of a cover letter) |
| change1_original_id  | Referencing the `original_id ` in the changes1 collection (change sets generated by grouping step 1 |
| change2_original_id  | Referencing the `original_id ` in the changes2 collection (change sets generated by grouping step 2 |
| mailing_list_original_id | Referencing the `original_id` in the mailinglists collection |
| series_original_id | Referencing the `original_id` in the series collection |
| new_series_original_id | Referencing the `original_id ` in the newseries collection |
| submitter_account_original_id | Referencing the `original_id` in the accounts collection |
| submitter_user_original_id | Referencing the `original_id ` in the users collection |
| project_original_id | Referencing the `original_id` in the projects collection |


#### Comments

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto increment id generated by Django |
| original_id | A combination of endpoint type, item type, and original Django id presented in the api data, e.g. `ffmpeg-comment-1` |
| msg_id      | Message id of the comment, which can be referenced to message id of the original email in the mailing list |
| msg_content | Content of the comment |
| date        | Date when the comment is submitted |
| subject     | Email subject of the comment |
| reply_to_msg_id | Message id of the patch that the comment replies to |
| web_url     | URL of the comment in patchwork |
| change1_original_id  | Referencing the `original_id ` in the changes1 collection (change sets generated by grouping step 1 |
| change2_original_id  | Referencing the `original_id ` in the changes2 collection (change sets generated by grouping step 2 |
| mailing_list_original_id | Referencing the `original_id` in the mailinglists collection |
| submitter_account_original_id | Referencing the `original_id` in the accounts collection |
| submitter_user_original_id | Referencing the `original_id ` in the users collection |
| patch_original_id | Referencing the `original_id` in the patches collection |
| project_original_id | Referencing the `original_id` in the projects collection |


#### NewSeries

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto increment id generated by Django |
| original_id | A combination of endpoint type, item type, and an auto-generated index, e.g. `ffmpeg-user-1` |
| cover_letter_msg_id | In-reply-to id of patches; Referenced by the `reply_to_msg_id` in the patches collection |
| project_original_id | Referencing the `original_id` in the projects collection |
| submitter_account_original_id | Referencing the `original_id` in the accounts collection |
| submitter_user_original_id | Referencing the `original_id ` in the users collection |
| series_original_id | Referencing the `original_id` in the series collection |
| inspection_needed | Indicating the corresponding data item might has some problems and manually checking might be needed |


#### Changes1/Changes2

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto increment id generated by Django |
| is_accepted | Whether the improved patch in the change set is accepted |
| parent_commit_id | Commit id of the previous version before this change is merged into the git repository |
| merged_commit_id | Commit id of the merge of this change into the git repository |
| commit_date | Date of commit |
| project_original_id | Referencing the `original_id` in the projects collection |
| submitter_account_original_id | Referencing the `original_id` in the accounts collection |
| submitter_user_original_id | Referencing the `original_id ` in the users collection |
| series_original_id | Referencing the `original_id` in the series collection |
| new_series_original_id | Referencing the `original_id ` in the newseries collection |
| inspection_needed | Indicating the corresponding data item might has some problems and manually checking might be needed |


#### MailingLists

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto increment id generated by Django |
| msg_id      | Message id of the email, referencing the `msg_id` of patches/comments |
| subject     | Email subject |
| content     | Email content |
| date        | Date when the email is sent |
| sender_name | Name of the sender of the email |
| web_url     | URL of the original email in the mailing list |
| project_original_id | Referencing the `original_id` in the projects collection |

### 3.1. Application filter

When accessing dataset via Python application, the fields that are available for filtering in each collection are different.

For filter type *exact* and *-*, directly use the field name to filter. For example, `id=1`.

For filter type *icontains*, *gt*, and *lt*, the filter type with two underlines in the front has to be added right after the field name. For instance, `original_id__icontains=ffmpeg`.

#### Accounts

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |
| username    | exact, icontains |
| email       | exact, icontains |
| user_original_id | exact |

#### Users

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |


#### Projects

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |
| name        | exact, icontains |


#### Series

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact            |
| original_id | exact, icontains |
| name        | exact, icontains |
| date        | gt, lt           |
| cover_letter_content_contain  | -     |
| project_original_id           | exact |
| submitter_account_original_id | exact |
| submitter_user_original_id    | exact |


#### Patches

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |
| name        | exact, icontains |
| state       | exact            |
| date        | gt, lt           |
| msg_content_contain | -     |
| code_diff_contain   | -     |
| commit_ref          | exact |
| change1_original_id | exact |
| change2_original_id | exact |
| mailing_list_original_id | exact |
| series_original_id       | exact |
| new_series_original_id   | exact |
| project_original_id      | exact |
| submitter_account_original_id | exact |
| submitter_user_original_id    | exact |


#### Comments

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |
| subject     | exact, icontains |
| date        | gt, lt           |
| msg_content_contain      | -     |
| change1_original_id      | exact |
| change2_original_id      | exact |
| mailing_list_original_id | exact |
| patch_original_id        | exact |
| project_original_id      | exact |
| submitter_account_original_id | exact |
| submitter_user_original_id    | exact |


#### NewSeries

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |
| project_original_id | exact |
| inspection_needed | exact |


#### Changes1/Changes2

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |
| is_accepted | exact |
| parent_commit_id | exact |
| merged_commit_id | exact |
| project_original_id | exact |
| inspection_needed | exact |


#### MailingLists

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |
| msg_id      | exact |
| subject     | exact |
| date        | gt, lt |
| sender_name | exact |
| project_original_id | exact |


