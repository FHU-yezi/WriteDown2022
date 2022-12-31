from pymongo import IndexModel, MongoClient

from utils.config import config


def init_DB(db_name: str):
    connection: MongoClient = MongoClient(config.db.host, config.db.port)
    db = connection[db_name]
    return db


db = init_DB(config.db.main_database)

run_log_db = db.run_log
access_log_db = db.access_log
user_data_db = db.user_data
timeline_data_db = db.timeline_data
heat_graph_data_db = db.heat_graph_data
wordcloud_graph_data_db = db.wordcloud_data

# 创建索引

# TODO
