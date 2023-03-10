from pymongo import IndexModel, MongoClient
from pymongo.database import Database

from utils.config import config


def init_db(db_name: str) -> Database:
    connection: MongoClient = MongoClient(config.db.host, config.db.port)
    return connection[db_name]


db = init_db(config.db.main_database)

run_log_db = db.run_log
access_log_db = db.access_log
user_db = db.user
timeline_db = db.timeline
heat_graph_db = db.heat_graph
wordcloud_db = db.wordcloud
interaction_type_db = db.interaction_type
interaction_per_hour_db = db.interaction_per_hour
interaction_summary_db = db.interaction_summary
on_rank_db = db.on_rank
general_data_db = db.general_data

article_fp_rank_db = init_db("JFetcherData").article_FP_rank

# 创建索引

user_db.create_indexes(
    [
        IndexModel([("status", 1)]),
        IndexModel([("user.slug", 1)], unique=True),
    ]
)
timeline_db.create_indexes(
    [
        IndexModel([("from_user", 1)]),
        IndexModel([("operation_type", 1)]),
        IndexModel([("operation_time", 1)]),
    ]
)
heat_graph_db.create_indexes(
    [
        IndexModel([("user_id", 1)], unique=True),
    ]
)
wordcloud_db.create_indexes(
    [
        IndexModel([("user_id", 1)], unique=True),
    ]
)
interaction_type_db.create_indexes(
    [
        IndexModel([("user_id", 1)], unique=True),
    ]
)
interaction_per_hour_db.create_indexes(
    [
        IndexModel([("user_id", 1)], unique=True),
    ]
)
interaction_summary_db.create_indexes(
    [
        IndexModel([("user_id", 1)], unique=True),
    ]
)
on_rank_db.create_indexes(
    [
        IndexModel([("user_id", 1)], unique=True),
    ]
)
