from typing import Dict

from data.heat_graph import HeatGraph
from data.user import User, UserStatus
from data.wordcloud import Wordcloud
from utils.db import timeline_data_db
from utils.word_split import get_word_freq


def analyze_active_data(user: User) -> None:
    if user.status != UserStatus.DONE:
        raise ValueError

    db_result = (
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

    data = {item["id"]: item["count"] for item in db_result}
    HeatGraph.create(user=user, data=data)


def analyze_comment_word_freq(user: User) -> None:
    if user.status != UserStatus.DONE:
        raise ValueError

    db_result = timeline_data_db.find(
        {
            "from_user": user.id,
            "operation_type": "comment_note",
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
