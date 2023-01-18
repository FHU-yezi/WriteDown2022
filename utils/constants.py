from typing import Dict, List

INTERACTION_NAME_MAPPING: Dict[str, str] = {
    "like_article": "点赞文章",
    "comment_article": "评论文章",
    "like_comment": "点赞评论",
    "follow_user": "关注用户",
    "publish_article": "发布文章",
    "follow_collection": "关注专题",
    "follow_notebook": "关注文集",
}

INTERACTION_ORDER: List[str] = [
    "like_article",
    "comment_article",
    "publish_article",
    "like_comment",
    "follow_user",
    "follow_collection",
    "follow_notebook",
]

INTERACTION_UNIT_TEXT: Dict[str, str] = {
    "like_article": "篇",
    "comment_article": "篇",
    "like_comment": "条",
    "follow_user": "人",
    "publish_article": "篇",
    "follow_collection": "个",
    "follow_notebook": "个",
}
