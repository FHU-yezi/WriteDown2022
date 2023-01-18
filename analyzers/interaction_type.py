from typing import Dict

from data.interaction_type import InteractionType
from data.user import User
from utils.db import timeline_db


def analyze_interaction_type(user: User) -> None:
    db_result = iter(
        timeline_db.aggregate(
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
    # “加入简书”不包含在互动类型图中
    if data.get("join_jianshu"):
        del data["join_jianshu"]

    InteractionType.create(
        user=user,
        data=data,
    )
