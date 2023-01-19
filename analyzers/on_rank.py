from typing import List

from data.on_rank import OnRank
from data.user import User
from utils.constants import DATA_STOP_TIME, DATA_STRAT_TIME
from utils.db import article_FP_rank_db, timeline_db


def analyze_on_rank(user: User) -> None:
    published_article_urls: List[str] = [
        x["url"]
        for x in timeline_db.aggregate(
            [
                {
                    "$match": {
                        "from_user": user.id,
                        "operation_type": "publish_article",
                    },
                },
                {
                    "$project": {
                        "_id": 0,
                        "url": "$target_article_url",
                    },
                },
            ],
        )
    ]

    # 用户没有发布过文章
    if not published_article_urls:
        OnRank.create(
            user=user,
            on_rank_count=0,
            top_ranking=None,
            articles_data=None,
        )

    on_rank_data = list(
        article_FP_rank_db.aggregate(
            [
                {
                    "$match": {
                        "article.url": {
                            "$in": published_article_urls,
                        },
                        "date": {
                            "$gte": DATA_STRAT_TIME,
                            "$lt": DATA_STOP_TIME,
                        },
                    },
                },
                {
                    "$project": {
                        "_id": 0,
                        "date": 1,
                        "ranking": 1,
                        "article_title": "$article.title",
                        "article_url": "$article.url",
                    },
                },
            ]
        )
    )

    OnRank.create(
        user=user,
        on_rank_count=len(on_rank_data),
        top_ranking=max([x["ranking"] for x in on_rank_data]) if len(on_rank_data) else None,
        articles_data=on_rank_data[:5],
    )
