from typing import Dict, List
from datetime import datetime

DATA_STRAT_TIME = datetime(2022, 1, 1, 0, 0, 0)
DATA_STOP_TIME = datetime(2022, 12, 31, 23, 59, 59)

INTERACTION_NAME_MAPPING: Dict[str, str] = {
    "like_article": "点赞文章",
    "comment_article": "评论文章",
    "like_comment": "点赞评论",
    "reward_article": "赞赏文章",
    "follow_user": "关注用户",
    "publish_article": "发布文章",
    "follow_collection": "关注专题",
    "follow_notebook": "关注文集",
}

INTERACTION_ORDER: List[str] = [
    "like_article",
    "comment_article",
    "publish_article",
    "reward_article",
    "like_comment",
    "follow_user",
    "follow_collection",
    "follow_notebook",
]

INTERACTION_UNIT_TEXT: Dict[str, str] = {
    "like_article": "篇",
    "comment_article": "次",
    "reward_article": "次",
    "like_comment": "条",
    "follow_user": "人",
    "publish_article": "篇",
    "follow_collection": "个",
    "follow_notebook": "个",
}

TEXT_REPORT_ITEM_NAME: Dict[str, str] = {
    "interaction_summary": "互动概览",
    "on_rank": "文章上榜记录",
}

GRAPH_REPORT_ITEM_NAME: Dict[str, str] = {
    "heat_graph": "互动热力图",
    "interaction_type": "互动类型图",
    "interaction_per_hour": "互动小时分布图",
    "wordcloud": "评论词云图",
}
