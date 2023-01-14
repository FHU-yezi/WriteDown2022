from typing import Any, Dict

from data.heat_graph import HeatGraph
from data.interaction_summary import InteractionSummary
from data.interaction_type_pie import InteractionTypePie
from data.user import User, UserStatus
from data.wordcloud import Wordcloud
from utils.db import timeline_data_db
from utils.log import run_logger
from utils.word_split import get_word_freq


def analyze_active_data(user: User) -> None:
    if user.status != UserStatus.DONE:
        raise ValueError

    db_result = iter(
        timeline_data_db.aggregate(
            [
                {
                    "$match": {
                        "from_user": user.id,
                    },
                },
                {
                    "$group": {
                        "_id": {
                            "$dateTrunc": {
                                "date": "$operation_time",
                                "unit": "day",
                            },
                        },
                        "count": {
                            "$sum": 1,
                        },
                    },
                },
                {
                    "$sort": {
                        "_id": 1,
                    },
                },
            ],
        ),
    )

    data = {item["_id"].isoformat(): item["count"] for item in db_result}
    HeatGraph.create(user=user, data=data)
    run_logger.debug(f"已完成对 {user.id} 的活跃度数据分析")


def analyze_comment_word_freq(user: User) -> None:
    if user.status != UserStatus.DONE:
        raise ValueError

    db_result = timeline_data_db.find(
        {
            "from_user": user.id,
            "operation_type": "comment_article",
        },
        {
            "_id": 0,
            "comment_content": 1,
        },
    )

    data: Dict[str, int] = dict(
        get_word_freq((x["comment_content"] for x in db_result))
    )
    Wordcloud.create(
        user=user,
        data=data,
    )
    run_logger.debug(f"已完成对 {user.id} 的评论词频数据分析")


def analyze_operation_type(user: User) -> None:
    if user.status != UserStatus.DONE:
        raise ValueError

    db_result = iter(
        timeline_data_db.aggregate(
            [
                {
                    "$match": {
                        "from_user": user.id,
                    },
                },
                {
                    "$group": {
                        "_id": "$operation_type",
                        "count": {
                            "$sum": 1,
                        },
                    },
                },
                {
                    "$sort": {
                        "count": -1,
                    },
                },
            ]
        )
    )

    data: Dict[str, int] = {x["_id"]: x["count"] for x in db_result}
    InteractionTypePie.create(user=user, data=data)
    run_logger.debug(f"已完成对 {user.id} 的互动类型数据分析")


def analyze_interaction_summary_data(user: User) -> None:
    likes_count: int = timeline_data_db.count_documents(
        {
            "from_user": user.id,
            "operation_type": "like_article",
        }
    )
    comments_count: int = timeline_data_db.count_documents(
        {
            "from_user": user.id,
            "operation_type": "comment_article",
        }
    )
    rewards_count: int = timeline_data_db.count_documents(
        {
            "from_user": user.id,
            "operation_type": "reward_article",
        }
    )
    subscribe_users_count: int = timeline_data_db.count_documents(
        {
            "from_user": user.id,
            "operation_type": "follow_user",
        }
    )
    publish_articles_count: int = timeline_data_db.count_documents(
        {
            "from_user": user.id,
            "operation_type": "publish_article",
        }
    )
    max_interactions_data: Dict[str, Any] = timeline_data_db.aggregate(
        [
            {
                "$match": {
                    "from_user": user.id,
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateTrunc": {
                            "date": "$operation_time",
                            "unit": "day",
                        },
                    },
                    "count": {
                        "$sum": 1,
                    },
                }
            },
            {
                "$sort": {
                    "count": -1,
                },
            },
            {
                "$limit": 1,
            },
        ]
    ).next()
    max_interactions_date = max_interactions_data["_id"]
    max_interactions_count = max_interactions_data["count"]
    del max_interactions_data

    max_likes_data: Dict[str, Any] = timeline_data_db.aggregate(
        [
            {
                "$match": {
                    "from_user": user.id,
                    "operation_type": "like_article",
                },
            },
            {
                "$group": {
                    "_id": {
                        "$dateTrunc": {
                            "date": "$operation_time",
                            "unit": "day",
                        }
                    },
                    "user_name": {
                        "$first": "$target_user_name",
                    },
                    "user_url": {
                        "$first": "$target_user_url",
                    },
                    "count": {
                        "$sum": 1,
                    },
                },
            },
            {
                "$sort": {
                    "count": -1,
                },
            },
            {
                "$match": {
                    "user_name": {
                        "$ne": "ordinary_player",
                    },
                },
            },
            {
                "$limit": 1,
            },
        ]
    ).next()
    max_likes_user_name = max_likes_data["user_name"]
    max_likes_user_url = max_likes_data["user_url"]
    max_likes_user_likes_count = max_likes_data["count"]
    del max_likes_data

    max_comments_data: Dict[str, Any] = timeline_data_db.aggregate(
        [
            {
                "$match": {
                    "from_user": user.id,
                    "operation_type": "comment_article",
                },
            },
            {
                "$group": {
                    "_id": {
                        "$dateTrunc": {
                            "date": "$operation_time",
                            "unit": "day",
                        }
                    },
                    "user_name": {
                        "$first": "$target_user_name",
                    },
                    "user_url": {
                        "$first": "$target_user_url",
                    },
                    "count": {
                        "$sum": 1,
                    },
                },
            },
            {
                "$sort": {
                    "count": -1,
                },
            },
            {
                "$match": {
                    "user_name": {
                        "$ne": "ordinary_player",
                    },
                },
            },
            {
                "$limit": 1,
            },
        ]
    ).next()
    max_comments_user_name = max_comments_data["user_name"]
    max_comments_user_url = max_comments_data["user_url"]
    max_comments_user_comments_count = max_comments_data["count"]
    del max_comments_data

    InteractionSummary.create(
        user=user,
        likes_count=likes_count,
        comments_count=comments_count,
        rewards_count=rewards_count,
        subscribe_users_count=subscribe_users_count,
        publish_articles_count=publish_articles_count,
        max_interactions_date=max_interactions_date,
        max_interactions_count=max_interactions_count,
        max_likes_user_name=max_likes_user_name,
        max_likes_user_url=max_likes_user_url,
        max_likes_user_likes_count=max_likes_user_likes_count,
        max_comments_user_name=max_comments_user_name,
        max_comments_user_url=max_comments_user_url,
        max_comments_user_comments_count=max_comments_user_comments_count,
    )
    run_logger.debug(f"已完成对 {user.id} 的互动总结数据分析")
