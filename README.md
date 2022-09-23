# Code-Review-Mining
This project consists of two parts: Django REST framework for accessing data and scrapy framework for crawling data.

## Tutorial

### How to deploy docker
Open the terminal and go to the directory where you clone the project
```command
cd docker

# build docker images
docker-compose build

# run docker containers
docker-compose up
```

### How to crawl data
#### Patchwork data
**1. Introduction**

There are three spiders for crawling patchwork data: PatchworkProjectSpider, PatchworkSeriesSpider, and PatchworkPatchSpider
- PatchworkProjectSpider (spider name: **patchwork_project**) crawls patchwork projects and corresponding maintainer accounts data
- PatchworkSeriesSpider (spider name: **patchwork_series**) crawls patchwork series and corresponding series submitter accounts data
- PatchworkPatchSpider (spider name: **patchwork_patch**) crawls patchwork patches, comments and corresponding submitter accounts data

To crawl data, open the terminal and run the following command to schedule a spider in scapyd
```command
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name>
```

**2. Customise spiders**

Each spider crawls patchwork api web page by item id (e.g. patch id -> https://patchwork.ffmpeg.org/api/patches/1). It automatically increases the item id to crawl the next web page util the id number reaches the default limit or the specified limit.

To specify the maximum item id to be crawled, pass an argument when running the command. You can also specify the start id and the endpoint to be crawled. (Currently the supported endpoint include kernel, ozlabs, and ffmpeg)
```command
# crawl projects
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name> -d start_project_id=<specified-id> -d end_project_id=<specified-id> -d org=<endpoint>

# crawl series
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name> -d start_series_id=<specified-id> -d end_series_id=<specified-id> -d org=<endpoint>

# crawl patches
curl http://localhost:6800/schedule.json -d project=default -d spider=<spider-name> -d start_patch_id=<specified-id> -d end_patch_id=<specified-id> -d org=<endpoint>
```

The retrieved data will be stored under /docker/scrapy_docker_app/retrieved_data
