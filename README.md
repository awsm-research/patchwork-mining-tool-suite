# Code-Review-Mining

## Introduction

This project provides a suite of tools for mining and further processing Patchwork data. It consists of three parts:
- Scrapy framework for crawling data
- Django REST framework for accessing and processing the data
- An application layer for manipulating data through Django

You can either crawl new data for yourself or directly use the provided dataset, which contains data of all sub-projects in FFmpeg, Ozlabs, and Kernel until 30/09/2022. The database we use in this project is MongoDB.
- If you would like to crawl data yourself, apply the Scrapy framework. The retrieved data will be stored in jsonlines files instead of directly being inserted to the database, so you will have to manually insert the data to the database with the help of the application layer. You can visit [How to crawl data](https://github.com/MingzhaoLiang/code-review-mining/wiki/How-to-crawl-data) for more information about crawling data.
- If you choose to use the provided dataset, simply deploy the docker and restore the database dump. For more information, visit [How to backup and restore data](https://github.com/MingzhaoLiang/Code-Review-Mining/wiki/How-to-backup-and-restore-data)

## Dataset

There are ten collections in the provided dataset, in which Projects, Accounts, Series, Patches, and Comments store the original retrieved data, and Users, Changes1, Changes2, NewSeries, and MailingLists record the results of processing. More details can be found at [data dictionary](https://github.com/MingzhaoLiang/code-review-mining/wiki/Data-dictionary).

## Tutorials

1. [How to deploy the docker](https://github.com/MingzhaoLiang/code-review-mining/wiki/How-to-deploy-the-docker)

2. [How to backup and restore data](https://github.com/MingzhaoLiang/Code-Review-Mining/wiki/How-to-backup-and-restore-data)

3. [How to crawl data](https://github.com/MingzhaoLiang/code-review-mining/wiki/How-to-crawl-data)

4. [How to retrieve data](https://github.com/MingzhaoLiang/Code-Review-Mining/wiki/How-to-retrieve-data)
