from pymongo import MongoClient
from mongoengine import connect

def mongoclient_connect(username, password, database_name, atlas_cluster="cluster0.hls0ye8.mongodb.net/", host_url="mongodb+srv://%s:%s@%s?retryWrites=true&w=majority"):

    client = MongoClient(host=host_url % (username, password, atlas_cluster))
    db_handle = client[db_name]
    
    return db_handle, client

def mongoengine_connect(username, password, database_name, atlas_cluster="cluster0.hls0ye8.mongodb.net/", host_url="mongodb+srv://%s:%s@%s?retryWrites=true&w=majority"):

    connect(database_name, host=host_url % (username, password, atlas_cluster))