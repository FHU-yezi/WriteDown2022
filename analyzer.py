from typing import Dict

from data.heat_graph import HeatGraph
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
