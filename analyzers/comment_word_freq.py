
from collections import Counter

from sspeedup.ability.word_split.jieba import AbilityJiebaPossegSplitterV1

from data.user import User
from data.wordcloud import Wordcloud
from utils.config import config
from utils.db import timeline_db

splitter = AbilityJiebaPossegSplitterV1(
    host=config.word_split_ability.host,
    port=config.word_split_ability.port,
    allowed_word_types_file="word_split_assets/allowed_word_types.txt",
)


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

    data = Counter()

    for item in db_result:
        data.update(splitter.get_word_freq(item["comment_content"]))

    data = dict(data)

    # 如果词频数据超过一千条，只保留词频数最大的一千条
    data = dict(tuple(data.items())[:1000])
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
