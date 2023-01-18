from typing import Dict

from data.user import User
from data.wordcloud import Wordcloud
from utils.db import timeline_db
from utils.word_split import get_word_freq, word_split_postprocess


def analyze_comment_word_freq(user: User) -> None:
    db_result = timeline_db.find(
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
    data = word_split_postprocess(data)
    total_comments_count: int = timeline_db.count_documents(
        {
            "from_user": user.id,
            "operation_type": "comment_article",
        }
    )
    Wordcloud.create(
        user=user,
        data=data,
        total_comments_count=total_comments_count,
    )
