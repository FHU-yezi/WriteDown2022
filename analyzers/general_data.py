from datetime import datetime, timedelta
from typing import Any, Dict, List

from JianshuResearchTools.convert import UserUrlToUserSlug

from data.general_analyze import GeneralData
from utils.db import heat_graph_db, user_db

ALL_DAYS_IN_2022 = tuple(datetime(2022, 1, 1) + timedelta(days=x) for x in range(365))
active_data_query_statements: Dict[str, Dict[str, str]] = {
    x.isoformat(): {"$sum": f"$data.{x.isoformat()}"} for x in ALL_DAYS_IN_2022
}


def get_total_users_count() -> int:
    return user_db.estimated_document_count()


def get_general_active_data() -> Dict[str, int]:
    db_result = list(
        heat_graph_db.aggregate(
            [
                {
                    "$group": {
                        "_id": None,
                        **active_data_query_statements,  # type: ignore[arg-type]
                    },
                },
            ],
        ),
    )[0]

    del db_result["_id"]
    return db_result


def get_popular_users_data() -> List[Dict[str, Any]]:
    db_result = iter(
        user_db.aggregate(
            [
                {
                    "$match": {
                        "status": 4,
                    },
                },
                {
                    "$project": {
                        "_id": 0,
                        "name": "$user.name",
                        "jianshu_url": "$user.url",
                        "view_count": "$result_show_count",
                    },
                },
                {
                    "$sort": {
                        "view_count": -1,
                    },
                },
                {
                    "$limit": 5,
                },
            ]
        )
    )

    result: List[Dict[str, Any]] = []
    # 加入 report_url
    for item in db_result:
        item["report_url"] = f"https://wd2022.sscreator.com/?app=report&user_slug={UserUrlToUserSlug(item['jianshu_url'])}"
        result.append(item)

    return result


def analyze_general_data() -> None:
    total_users_count: int = get_total_users_count()
    general_active_data: Dict[str, int] = get_general_active_data()
    popular_users_data: List[Dict[str, Any]] = get_popular_users_data()

    GeneralData.db.delete_many({})  # 清空之前的统计数据
    GeneralData.create(
        total_users_count=total_users_count,
        active_data=general_active_data,
        popular_users_data=popular_users_data,
    )
