from typing import Any, Dict

from data.interaction_summary import InteractionSummary
from data.user import User
from utils.db import timeline_db


def analyze_interaction_summary_data(user: User) -> None:
    try:
        max_interactions_data: Dict[str, Any] = timeline_db.aggregate(
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
    except StopIteration:
        max_interactions_date = None
        max_interactions_count = None
    else:
        max_interactions_date = max_interactions_data["_id"]
        max_interactions_count = max_interactions_data["count"]

    try:
        max_likes_data: Dict[str, Any] = timeline_db.aggregate(
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
                    "$match": {
                        "_id": {
                            "$ne": user.url,
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
    except StopIteration:
        max_likes_user_name = None
        max_likes_user_url = None
        max_likes_user_likes_count = None
    else:
        max_likes_user_name = max_likes_data["name"]
        max_likes_user_url = max_likes_data["_id"]
        max_likes_user_likes_count = max_likes_data["count"]
        del max_likes_data

    try:
        max_comments_data: Dict[str, Any] = timeline_db.aggregate(
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
                    "$match": {
                        "_id": {
                            "$ne": user.url,
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
    except StopIteration:
        max_comments_user_name = None
        max_comments_user_url = None
        max_comments_user_comments_count = None
    else:
        max_comments_user_name = max_comments_data["name"]
        max_comments_user_url = max_comments_data["_id"]
        max_comments_user_comments_count = max_comments_data["count"]
        del max_comments_data

    interactions_data: Dict[str, int] = {
        x["_id"]: x["count"]
        for x in timeline_db.aggregate(
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
            ],
        )
    }
    if interactions_data.get("join_jianshu"):
        del interactions_data["join_jianshu"]

    InteractionSummary.create(
        user=user,
        interactions_data=interactions_data,
        max_interactions_date=max_interactions_date,
        max_interactions_count=max_interactions_count,
        max_likes_user_name=max_likes_user_name,
        max_likes_user_url=max_likes_user_url,
        max_likes_user_likes_count=max_likes_user_likes_count,
        max_comments_user_name=max_comments_user_name,
        max_comments_user_url=max_comments_user_url,
        max_comments_user_comments_count=max_comments_user_comments_count,
    )
