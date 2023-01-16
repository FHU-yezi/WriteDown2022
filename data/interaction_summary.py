from datetime import datetime
from typing import Dict

from bson import ObjectId

from data._base import DataModel
from utils.db import interaction_summary_data_db
from utils.dict_helper import get_reversed_dict
from utils.html import link


class InteractionSummary(DataModel):
    db = interaction_summary_data_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "user_id": "user_id",
        "likes_count": "interactions.likes_count",
        "comments_count": "interactions.comments_count",
        "rewards_count": "interactions.rewards_count",
        "subscribe_users_count": "interactions.subscribe_users_count",
        "publish_articles_count": "interactions.publish_articles_count",
        "max_interactions_date": "max_interactions.date",
        "max_interactions_count": "max_interactions.count",
        "max_likes_user_name": "max_likes.user_name",
        "max_likes_user_url": "max_likes.user_url",
        "max_likes_user_likes_count": "max_likes.likes_count",
        "max_comments_user_name": "max_comments.user_name",
        "max_comments_user_url": "max_comments.user_url",
        "max_comments_user_comments_count": "max_comments.comments_count",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,
        user_id: str,
        likes_count: int,
        comments_count: int,
        rewards_count: int,
        subscribe_users_count: int,
        publish_articles_count: int,
        max_interactions_date: datetime,
        max_interactions_count: int,
        max_likes_user_name: str,
        max_likes_user_url: str,
        max_likes_user_likes_count: int,
        max_comments_user_name: str,
        max_comments_user_url: str,
        max_comments_user_comments_count: int,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.likes_count = likes_count
        self.comments_count = comments_count
        self.rewards_count = rewards_count
        self.subscribe_users_count = subscribe_users_count
        self.publish_articles_count = publish_articles_count
        self.max_interactions_date = max_interactions_date
        self.max_interactions_count = max_interactions_count
        self.max_likes_user_name = max_likes_user_name
        self.max_likes_user_url = max_likes_user_url
        self.max_likes_user_likes_count = max_likes_user_likes_count
        self.max_comments_user_name = max_comments_user_name
        self.max_comments_user_url = max_comments_user_url
        self.max_comments_user_comments_count = max_comments_user_comments_count

        super().__init__()

    @classmethod
    def from_id(cls, id: str) -> "InteractionSummary":
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @classmethod
    def from_user_id(cls, user_id: str) -> "InteractionSummary":
        db_data = cls.db.find_one({"user_id": user_id})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data)

    @property
    def user(self):
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def create(
        cls,
        user,
        likes_count: int,
        comments_count: int,
        rewards_count: int,
        subscribe_users_count: int,
        publish_articles_count: int,
        max_interactions_date: datetime,
        max_interactions_count: int,
        max_likes_user_name: str,
        max_likes_user_url: str,
        max_likes_user_likes_count: int,
        max_comments_user_name: str,
        max_comments_user_url: str,
        max_comments_user_comments_count: int,
    ) -> "InteractionSummary":
        insert_result = cls.db.insert_one(
            {
                "user_id": user.id,
                "interactions.likes_count": likes_count,
                "interactions.comments_count": comments_count,
                "interactions.rewards_count": rewards_count,
                "interactions.subscribe_users_count": subscribe_users_count,
                "interactions.publish_articles_count": publish_articles_count,
                "max_interactions.date": max_interactions_date,
                "max_interactions.count": max_interactions_count,
                "max_likes.user_name": max_likes_user_name,
                "max_likes.user_url": max_likes_user_url,
                "max_likes.likes_count": max_likes_user_likes_count,
                "max_comments.user_name": max_comments_user_name,
                "max_comments.user_url": max_comments_user_url,
                "max_comments.comments_count": max_comments_user_comments_count,
            },
        )

        return cls.from_id(insert_result.inserted_id)

    def get_summary(self) -> str:
        user = self.user

        return f"""
        {link(user.name, user.url, new_window=True)}，你的 2022 互动总结如下：

        - 点赞：{self.likes_count} 次
        - 评论：{self.comments_count} 次
        - 打赏：{self.rewards_count} 次
        - 关注用户：{self.subscribe_users_count} 人
        - 发布文章：{self.publish_articles_count} 篇

        你互动量最多的一天是 {self.max_interactions_date.date()}，这一天你在社区进行了 {self.max_interactions_count} 次互动。

        你最喜欢给 {link(self.max_likes_user_name, self.max_likes_user_url, new_window=True)} 的文章点赞，这一年你为 TA 送上了 {self.max_likes_user_likes_count} 个赞。

        你最喜欢评论 {link(self.max_comments_user_name, self.max_comments_user_url, new_window=True)} 的文章，这一年你在 TA 的文章下评论了 {self.max_comments_user_comments_count} 次。
        """
