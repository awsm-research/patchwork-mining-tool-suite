# Curated Email-Based Code Reviews Datasets
Code review is an important practice that improves the overall quality of a proposed patch (i.e., a code change). While much research
focused on tool-based code reviews (e.g., a Gerrit code review tool, GitHub), many traditional open-source software (OSS) projects still conduct code review through emails. However, due to the nature of unstructured email-based data, it can be challenging to mine email-based code reviews, hindering researchers from delving into the code review practice of such long-standing OSS projects. Therefore, this paper presents large-scale datasets of email-based code reviews of 160 projects across three OSS communities (i.e., FFmpeg, OzLabs, and Linux Kernel). We mined the data from Patchwork, a web-based patch-tracking system for email-based code review, and curated the data by grouping a submitted patch and its revised versions and grouping email aliases. Our datasets include a total of 3.8M patches with 1.9M patch groups and 155K email addresses belong to 130K individuals. Our published artefacts include the datasets as well as a tool suite to crawl, curate, and store Patchwork data. With our datasets, future work can directly delve into an email-based code review practice of large OSS projects without additional effort in data collection and curation.

## Introduction

This project provides a suite of tools for mining and further processing Patchwork data. It consists of three parts:
- Scrapy framework for crawling data
- Django REST framework and Python application for accessing and processing the data
- MongoDB database for storing the data

## Table of Content
1. [Heuristics and evaluation results](#1-heuristics-and-evaluation-results)
2. [Provided dataset](#2-provided-dataset)
    1. [Get provided dataset](#21-get-provided-dataset)
    2. [Analyse provided dataset](#22-analyse-provided-dataset)
3. [Data crawling](#3-data-crawling)
    1. [Basic steps for crawling](#31-basic-steps-for-crawling)
        1. [Schedule spiders on scrapyd](#311-schedule-spiders-on-scrapyd)
        2. [Run spiders from script](#312-run-spiders-from-script)
        3. [Run spiders using commands](#313-run-spiders-using-commands)
    2. [Customise spiders](#32-customise-spiders)
        1. [Customise spiders in scrapyd](#321-customise-spiders-in-scrapyd)
        2. [Customise spiders from script](#322-customise-spiders-from-script)
        3. [Customise spiders run using commands](#323-customise-spiders-run-using-commands)
    3. [Insert data to database](#33-insert-data-to-database)
4. [Data dictionary](#4-data-dictionary)
    1. [Application filter](#41-application-filter)


## 1. Heuristics and evaluation results

A [sample](./app/implementation.ipynb) for processing the raw crawled data, including identity grouping and patch grouping, and [another](./app/import_data.ipynb) for importing processed data to the database are provided in Jupyter notebook, which can be founf in folder app.

### 1.1 Patch grouping heuristic constraints

Two heuristics, Exact Bags-of-Words (BoW) Grouping and One-word Difference Grouping, are implemented for patch grouping. 
Below are the constraints for the heuristics.

**Exact BoW Grouping**
* The bag-of-words of the summary phrases of the patches are the same
* The patches do not belong to the same series

**One-word Difference Grouping**
* The bag of words of a group should be different from that of another group by one word
* The different word should not be "revert"
* Version references of both groups should not be intersected
* Both groups contain at least one common patch submitter

### 1.2 Evaluation results

**Accuracy of grouping**

For our manual evaluation, a patch grouping is considered correct if all patches in the group are related to the same review process by investigating the content of each patch (e.g., commit message, related comments, code changes).
Similarly, we consider an individual identification as correct if all the identities in the group are certainly from the same individual by examining whether 1) the identities have submitted patches in the same group, 2) the identities have commented on the same patches, and 3) the identities share other characteristics such as the organisation email addresses.
Finally, we compute the grouping accuracy using the following calculation:
% The metric used in the evaluation is accuracy, which is calculated in the following manner:

$`Accuracy = \frac{\text{\#Correct groups}}{\text{\#Evaluated groups}}`$

where correct groups refer to 1) groups of patches that belong to the same code review process or 2) groups of identities that belong to the same individual that are correctly identified; and evaluated groups refer to the sampled groups that are manually evaluated.

Below is the accuracy of each heuristic applied to the selected five projects.

| Projects         | Exact BoW grouping | One-word difference grouping | Individual grouping |
| :--------------- | :----------------- | :--------------------------- | :------------------ |
| FFmpeg           | 96.68%(&plusmn;5%) | 81.68%(&plusmn;5%) | 89.29%(&plusmn;5%) |
| QEMU             | 100.00%(&plusmn;5%)| 90.94%(&plusmn;5%) | 88.41%(&plusmn;5%) |
| U-Boot           | 99.47%(&plusmn;5%) | 92.48%(&plusmn;5%) | 86.45%(&plusmn;5%) |
| Linux Arm Kernel | 99.74%(&plusmn;5%) | 87.77%(&plusmn;5%) | 90.91%(&plusmn;5%) |
| Netdev + BPF     | 99.47%(&plusmn;5%) | 82.51%(&plusmn;5%) | 94.01%(&plusmn;5%) |

## 2. Provided dataset
The provided dataset contains data of all projects from the three OSS communities, including [FFmpeg](https://patchwork.ffmpeg.org/project/ffmpeg/list/), [Ozlabs](http://patchwork.ozlabs.org), and [Linux Kernel](https://patchwork.kernel.org), until 30/09/2022. There are ten collections in which Project, Identity, Series, Patche, Comment, and MailingList store the original crawled data (some fields will be updated during further processing), and Individual, Change1, Change2, and NewSeries record the results of processing. 

### 2.1. Get provided dataset
The compressed complete dataset can be downloaded [here](https://figshare.com/s/457abb97f75656229829). Decompress the downloaded file in root folder of the project to use in the folowing step.

### 2.2. Use provided dataset
To use the provided dataset, simply run docker containers without migrating database by using following commands in the terminal. 
```command
cd app/docker

# build docker images
docker-compose -f docker-compose-non-migrate.yml build 

# run docker containers
docker-compose -f docker-compose-non-migrate.yml up -d
```

To run certain services in docker, specify service names, i.e. ```docker-compose -f docker-compose-non-migrate.yml up <service_name> <service_name> -d```

Then, restore the database by running following command.
```command
docker exec -i mongodb_docker_container sh -c 'exec mongorestore --archive --nsInclude=code_review_db.*' < /path/to/code_review_db.archive
```

After restoration process is done, Mongodb database will be available for local access at `mongodb://localhost:27017`. 

#### 2.2.1. Access database directly
The sample analyses on code review metrics in a Jupyter [notebook](./analysis/review-analysis.ipynb) and their outputs can be found in folder analysis.

#### 2.2.2. Access database via Python application

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

## 3. Data crawling
To crawl new data from the source, apply the Scrapy framework in the suite. Retrieved data will be first stored in jsonlines files. The file content can be inserted into the database with the help of the application layer. 

There are three spiders for crawling patchwork data. Their **spider names** are **patchwork_project**, **patchwork_series**, and **patchwork_patch**.
- *patchwork_project crawls patchwork projects and corresponding maintainer accounts data.*
- *patchwork_series crawls patchwork series and corresponding series submitter accounts data.*
- *patchwork_patch crawls patchwork patches, comments and corresponding submitter accounts data.*

The retrieved data will be stored under `/docker/scrapy_docker_app/retrieved_data`.

### 3.1. Basic steps for crawling
There are three ways to run spiders.
* Schedule spiders on scrapyd
* Run spiders from a script
* Run spiders using commands.

#### 3.1.1. Schedule spiders on scrapyd
Run the docker containers by entering following commands in terminal. 
```command
cd docker

# build docker images
docker-compose -f docker-compose.yml build 

# run docker containers
docker-compose -f docker-compose.yml up -d
```
To run certain services in docker, specify service names, i.e. ```docker-compose -f docker-compose.yml up <service_name> <service_name> -d```

Then, run the following command to schedule and run a spider in scapyd. Multiple spiders can be run and manage by scrapyd.
```command
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name>
```

#### 3.1.2. Run spiders from script

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

#### 3.1.3. Run spiders using commands

Run the following command in the **container terminal**.
```command
scrapy crawl <spider-name>
```

### 3.2. Customise spiders

Each spider crawls patchwork api web page by item id (e.g. patch id -> `https://patchwork.ffmpeg.org/api/patches/1/`). It automatically increases the item id to crawl the next web page until the id number reaches the default limit or the specified limit. The start id and the endpoint to be crawled can be specified, if necessary.


#### 3.2.1. Customise spiders in scrapyd

Pass arguments in the command. **Each argument should follow an option `-d`.**

```command
# crawl projects
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name> -d start_project_id=<specified-id> -d end_project_id=<specified-id> -d endpoint_type=<endpoint-name>

# crawl series
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name> -d start_series_id=<specified-id> -d end_series_id=<specified-id> -d endpoint_type =<endpoint-name>

# crawl patches
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name> -d start_patch_id=<specified-id> -d end_patch_id=<specified-id> -d endpoint_type =<endpoint-name>
```

#### 3.2.2. Customise spiders from script

In the provided structure, specify the argument in the crawlers.

```python
@defer.inlineCallbacks
    def crawl():
        yield runner.crawl(PatchworkProjectSpider, start_project_id=..., end_project_id=..., endpoint_type=...)
        yield runner.crawl(PatchworkSeriesSpider, start_series_id=..., end_series_id=..., endpoint_type=...)
        yield runner.crawl(PatchworkPatchSpider, start_patch_id=..., end_patch_id=..., endpoint_type=...)
        reactor.stop()
```

#### 3.2.3. Customise spiders run using commands

Similar to customisation in scrapyd, with the argument option `-a`
```command
# take crawling project as an example
scrapy crawl <spider-name> -a start_project_id=<specified-id> -a end_project_id=<specified-id> -a endpoint_type=<endpoint-name>
```

### 3.3. Insert data to database
After crawling data from Patchwork, relevant data can be inserted to the database with the help of the application layer.

#### 3.3.1. Process data

Two classes are provided in the application layer to assist with access and process data.

One is AccessData, which helps 1) to insert data into the database; 2) to access json files in your local machine; 3) to query data from the database.

The other is ProcessInitialData, which helps 1) to identify individual (i.e. unique developers) within each project; and 2) to group related code review activities of the same proposed patch.

It is adivised to run the two automated approaches provided in ProcessInitialData before data insertion.

Load the data before running the approaches. Json files can be immediately accessed with the help of ```load_json()``` provided in AccessData.

```python
import application_layer

access_data = application_layer.AccessData()

# load identity data
project_identity_data = access_data.load_json("path/to/crawled/project/identity/data")
series_identity_data = access_data.load_json("path/to/crawled/series/identity/data")
patch_identity_data = access_data.load_json("path/to/crawled/patch/identity/data")

# combine identity data
identity_data = project_identity_data + series_identity_data + patch_identity_data

# load series data
series_data = access_data.load_json("path/to/crawled/series/data")

# load patch data
patch_data = access_data.load_json("path/to/crawled/patch/data")

# load comment data
comment_data = access_data.load_json("path/to/crawled/comment/data")
```

After loading the data, instantiate ProcessInitialData to run the approaches.

```python
process_data = application_layer.ProcessInitialData()
```

However, newseries, change1, change2, and individual data are newly generated data and they do not have original id as those crawled from Patchwork (See data attributes in the [data dictionary](#3-data-dictionary)), so their initial original ids are required to be specified **if the approaches are not run at the first time**.

To specify the original ids, you can retrieve the corresponding maximum original id from the database.

```python
import pymongo, application layer

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["code_review_db"]

newseries_original_id = db.patchwork_newseries.count_documents({}) + 1
change1_original_id = db.patchwork_change1.count_documents({}) + 1
change2_original_id = db.patchwork_change2.count_documents({}) + 1
individual_original_id = db.patchwork_individual.count_documents({}) + 1

process_data = application_layer.ProcessInitialData(newseries_original_id, change1_original_id, change2_original_id, individual_original_id)
```

Or you can specify a specific number.

```python
process_data = application_layer.ProcessInitialData(newseries_original_id=10, change1_original_id=10, change2_original_id=10, individual_original_id=10)
```

To run the two approaches, simply run the ```process_data()``` function.
```python
individual_data, updated_series_data, updated_patch_data, updated_comment_data, newseries_data, change1_data, change2_data = process_data.process_data(identity_data, series_data, patch_data, comment_data)
```

#### 3.3.2. Insert data
Data can be inserted to the database by using the ```insert_data()``` function provided in ```AccessData```. Specifically, specify the data to be inserted or the location of the data to be inserted, and its corresponding item type. The item type include identity, project, individual, series, newseries, change1, change2, patch, and comment.

```python

# data has been loaded before insertion
access_data.insert_data(data=project_data, item_type="project")

# data has not been loaded before insertion
access_data.insert_data(data="path/to/project/data", item_type="project")
```

However, the insertion of each item type should follow a specific order: identity -> project -> individual -> series -> newseries -> change1 -> change2 -> patch -> comment, unless you confirm that related foreign key data in the data to be inserted are already in the database (See the [complete ER diagram](#3-data-dictionary)).

## 4. Data dictionary

This section describes the high-level structure of the dataset. (**Note that fields named change1 refer to ExactBoWGroup and those named change2 refer to OWDiffGroup**)

Below is a complete ER diagram depicting the database structure, which can also be accessed in [dbdiagram](https://dbdiagram.io/d/dbdiagram-io-complete-656eb11f56d8064ca0638684).

![text](https://github.com/MingzhaoLiang/Code-Review-Mining/blob/main/figures/dbdiagram-io-complete.png)

### Collections
- [Identity](#Identity)
- [Individual](#Individual)
- [Project](#Project)
- [Series](#Series)
- [Patch](#Patch)
- [Comment](#Comment)
- [NewSeries](#NewSerie)
- [Change1/Change2](#Change1Change2)
- [MailingList](#MailingList)


#### Identity

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of OSS community name, item type, and original Django id presented in the api data, e.g. `ffmpeg-people-1`; Note that for maintainer identities of a project, the item type is `user`, e.g. `ffmpeg-user-1` |
| email       | Email of the identity |
| name        | Name of the identity  |
| api_url     | API URL for retrieving the original data in patchwork (Authentication needed as patchwork blocks the access) |

#### Individual

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of OSS community name, item type, and an auto-generated index, e.g. `ffmpeg-individual-1` |
| project     | The project in which this individual has submitted patches, comments, etc. |
| identity    | Idenities which belong to the same individual in a project |


#### Project

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of OSS community name, item type, and original Django id presented in the api data, e.g. `ffmpeg-project-1` |
| name        | Name of the project |
| repository_url | URL of the git repository of the project if applicable |
| api_url     | API URL for retrieving the project data in patchwork |
| web_url     | URL of the project web page (if applicable) |
| list_id     | Id of the mailing list of the project |
| list_address | Email address of the mailing list of the project |
| maintainer_identity | Maintainers' corresponding identity detail |


#### Series

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of OSS community name, item type, and original Django id presented in the api data, e.g. `ffmpeg-series-1` |
| name        | Name of the series (maybe null) |
| date        | Created date of the series      |
| version     | Version of the series           |
| total       | Number of patches submitted under the series |
| received_total | Number of patches submitted under the series and received by the mailing list |
| cover_letter_msg_id | Message id of the cover letter email (the email that all following patch emails reply to) |
| cover_letter_content | Content of the cover letter email (maybe null) |
| api_url | API URL for retrieving the series data in patchwork |
| web_url | URL of the series in patchwork |
| project | Detail of the project that this series belong to |
| submitter_identity | Submitter's identity detail |
| submitter_individual | Submitter's individual detail |


#### Patch

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of OSS community name, item type, and original Django id presented in the api data, e.g. `ffmpeg-patch-1` |
| name        | Name of the patch |
| state       | Status of the patch (accepted, superseded, new, etc.) |
| date        | Date when the patch is submitted |
| msg_id      | Message id of the patch, which can be referenced to message id of the original email in the mailing list |
| msg_content | Message content of the patch |
| code_diff   | Differences of the code changes in the patch |
| api_url     | API URL for retrieving the patch data in patchwork |
| web_url     | URL of the patch in patchwork |
| commit_ref  | Commit id in the corresponding git repository |
| in_reply_to | Message id of the email that the patch replies to (in most cases, it is the msg_id of a cover letter) |
| change1  | Referencing the `original_id ` in the ExactBoWGroup collection (generated by Exact BoW Grouping) |
| change2  | Referencing the `original_id ` in the OWDiffGroup collection (generated by One-word Difference Grouping) |
| mailinglist | Referencing the `original_id` in the mailinglists collection |
| series | Referencing the `original_id` in the series collection |
| newseries | Referencing the `original_id ` in the newseries collection |
| submitter_identity | Referencing the `original_id` in the accounts collection |
| submitter_individual | Referencing the `original_id ` in the users collection |
| project | Referencing the `original_id` in the projects collection |


#### Comment

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of OSS community name, item type, and original Django id presented in the api data, e.g. `ffmpeg-comment-1` |
| msg_id      | Message id of the comment, which can be referenced to message id of the original email in the mailing list |
| msg_content | Content of the comment |
| date        | Date when the comment is submitted |
| subject     | Email subject of the comment |
| reply_to_msg_id | Message id of the patch that the comment replies to |
| web_url     | URL of the comment in patchwork |
| change1  | Referencing the `original_id ` in the ExactBoWGroup collection (generated by Exact BoW Grouping) |
| change2  | Referencing the `original_id ` in the OWDiffGroup collection (generated by One-word Difference Grouping) |
| mailinglist | Referencing the `original_id` in the mailinglists collection |
| submitter_identity | Referencing the `original_id` in the accounts collection |
| submitter_individual | Referencing the `original_id ` in the users collection |
| patch | Referencing the `original_id` in the patches collection |
| project | Referencing the `original_id` in the projects collection |


#### NewSeries

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of OSS community name, item type, and an auto-generated index, e.g. `ffmpeg-newseries-1` |
| cover_letter_msg_id | In-reply-to id of patches; Referenced by the `reply_to_msg_id` in the patches collection |
| project | Referencing the `original_id` in the projects collection |
| submitter_identity | Referencing the `original_id` in the accounts collection |
| submitter_individual | Referencing the `original_id ` in the users collection |
| series | Referencing the `original_id` in the series collection |
| inspection_needed | Indicating the corresponding data item might has some problems and manually checking might be needed |


#### ExactBoWGroup / OWDiffGroup

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of OSS community name, item type, and an auto-generated index, e.g. `ffmpeg-change1-1`, `ffmpeg-change2-1` |
| is_accepted | Whether the improved patch in the change set is accepted |
| parent_commit_id | Commit id of the previous version before this change is merged into the git repository |
| merged_commit_id | Commit id of the merge of this change into the git repository |
| commit_date | Date of commit |
| project | Referencing the `original_id` in the projects collection |
| submitter_identity | Referencing the `original_id` in the accounts collection |
| submitter_individual | Referencing the `original_id ` in the users collection |
| series | Referencing the `original_id` in the series collection |
| newseries | Referencing the `original_id ` in the newseries collection |
| inspection_needed | Indicating the corresponding data item might has some problems and manually checking might be needed |
| patches | detail of list of related patches |
| comments | detail of list of related comments |


#### MailingList

| Fields      | Description |
| :---------- | :---------- |
| _id         | Object id created by MongoDB |
| id          | Auto-increment id generated by Django |
| original_id | A combination of OSS community name, item type, and an auto-generated index, e.g. `ffmpeg-mailinglist-1` |
| msg_id      | Message id of the email, referencing the `msg_id` of patches/comments |
| subject     | Email subject |
| content     | Email content |
| date        | Date when the email is sent |
| sender_name | Name of the sender of the email |
| web_url     | URL of the original email in the mailing list |
| project | Referencing the `original_id` in the projects collection |

### 4.1. Application filter

When accessing dataset via Python application, the fields that are available for filtering in each collection are different.

For filter type *exact* and *-*, directly use the field name to filter. For example, `id=1`.

For filter type *icontains*, *gt*, and *lt*, the filter type with two underlines in the front has to be added right after the field name. For instance, `original_id__icontains=ffmpeg`.

#### Identity

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |
| username    | exact, icontains |
| email       | exact, icontains |
| user_original_id | exact |

#### Individual

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |


#### Project

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


#### Patch

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


#### Comment

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


#### ExactBoWGroup / OWDiffGroup

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |
| is_accepted | exact |
| parent_commit_id | exact |
| merged_commit_id | exact |
| project_original_id | exact |
| inspection_needed | exact |


#### MailingList

| Available field | Available filter type |
| :-------------- | :-------------------- |
| id          | exact |
| original_id | exact, icontains |
| msg_id      | exact |
| subject     | exact |
| date        | gt, lt |
| sender_name | exact |
| project_original_id | exact |


