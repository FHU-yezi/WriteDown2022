from typing import Any, Callable, Dict

from data.heat_graph import HeatGraph
from data.interaction_per_hour import InteractionPerHour
from data.interaction_summary import InteractionSummary
from data.interaction_type import InteractionType
from data.user import User
from data.wordcloud import Wordcloud
from utils.db import timeline_data_db
from utils.word_split import get_word_freq


def analyze_active_data(user: User) -> None:
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


def analyze_comment_word_freq(user: User) -> None:
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


def analyze_interaction_type(user: User) -> None:
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
    InteractionType.create(user=user, data=data)


def analyze_interaction_per_hour_data(user: User) -> None:
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
                            "$hour": "$operation_time",
                        },
                        "count": {
                            "$sum": 1,
                        },
                    }
                },
                {
                    "$sort": {
                        "_id": 1,
                    },
                },
            ],
        )
    )

    # 不能使用整数作为键，此处进行类型转换
    data: Dict[str, int] = {str(x["_id"]): x["count"] for x in db_result}
    InteractionPerHour.create(
        user=user,
        data=data,
    )


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
                    "_id": "$target_user_url",
                    "name": {
                        "$first": "$target_user_name",
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
                "$limit": 1,
            },
        ]
    ).next()
    max_likes_user_name = max_likes_data["name"]
    max_likes_user_url = max_likes_data["_id"]
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
                    "_id": "$target_user_url",
                    "name": {
                        "$first": "$target_user_name",
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
                "$limit": 1,
            },
        ]
    ).next()
    max_comments_user_name = max_comments_data["name"]
    max_comments_user_url = max_comments_data["_id"]
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


ANALYZE_FUNCS: Dict[str, Callable[[User], None]] = {
    "活跃度数据": analyze_active_data,
    "评论词频数据": analyze_comment_word_freq,
    "互动类型数据": analyze_interaction_type,
    "互动小时分布数据": analyze_interaction_per_hour_data,
    "互动总结数据": analyze_interaction_summary_data,
}
