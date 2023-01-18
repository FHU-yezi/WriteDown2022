from data.heat_graph import HeatGraph
from data.user import User
from utils.db import timeline_db


def analyze_active_data(user: User) -> None:
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
    HeatGraph.create(
        user=user,
        data=data,
    )
