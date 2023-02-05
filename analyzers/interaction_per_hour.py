from typing import TYPE_CHECKING, Dict

from data.interaction_per_hour import InteractionPerHour
from utils.db import timeline_db

if TYPE_CHECKING:
    from data.user import User


def analyze_interaction_per_hour(user: User) -> None:
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

    # 对没有互动的小时补 0
    # 不能使用整数作为键，此处进行类型转换
    data: Dict[str, int] = {str(x): 0 for x in range(24)}
    data.update({str(x["_id"]): x["count"] for x in db_result})
    InteractionPerHour.create(
        user=user,
        data=data,
    )
