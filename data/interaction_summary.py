from typing import TYPE_CHECKING, Dict, Optional

from bson import ObjectId

from data._base import DataModel
from utils.constants import (
    INTERACTION_NAME_MAPPING,
    INTERACTION_ORDER,
    INTERACTION_UNIT_TEXT,
)
from utils.db import interaction_summary_db
from utils.dict_helper import get_reversed_dict
from utils.html import link

if TYPE_CHECKING:
    from datetime import datetime

    from data.user import User

class InteractionSummary(DataModel):
    db = interaction_summary_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "user_id": "user_id",
        "is_aviliable": "is_aviliable",
        "interactions_data": "interactions_data",
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
        id: str,  # noqa
        user_id: str,
        is_aviliable: bool,
        interactions_data: Dict[str, int],
        max_interactions_date: Optional[datetime],
        max_interactions_count: Optional[int],
        max_likes_user_name: Optional[str],
        max_likes_user_url: Optional[str],
        max_likes_user_likes_count: Optional[int],
        max_comments_user_name: Optional[str],
        max_comments_user_url: Optional[str],
        max_comments_user_comments_count: Optional[int],
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.is_aviliable = is_aviliable
        self.interactions_data = interactions_data
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
    def from_id(cls, id: str) -> "InteractionSummary":  # noqa
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @classmethod
    def from_user_id(cls, user_id: str) -> "InteractionSummary":
        db_data = cls.db.find_one({"user_id": user_id})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @property
    def user(self) -> User:
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def create(
        cls,
        user: User,
        interactions_data: Dict[str, int],
        max_interactions_date: Optional[datetime],
        max_interactions_count: Optional[int],
        max_likes_user_name: Optional[str],
        max_likes_user_url: Optional[str],
        max_likes_user_likes_count: Optional[int],
        max_comments_user_name: Optional[str],
        max_comments_user_url: Optional[str],
        max_comments_user_comments_count: Optional[int],
    ) -> "InteractionSummary":
        insert_result = cls.db.insert_one(
            {
                "user_id": user.id,
                "is_aviliable": True,
                "interactions_data": interactions_data,
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

    def get_report(self) -> str:
        user = self.user

        welcome_part = f"{link(user.name, user.url, new_window=True)}，你的 2022 互动总结如下："

        if self.interactions_data:
            interaction_types_detail_part = "- " + "\n- ".join(
                [
                    (
                        f"{INTERACTION_NAME_MAPPING.get(key, key)}："
                        f"{value} "
                        f"{INTERACTION_UNIT_TEXT.get(key, '次')}"
                    )
                    for key, value in dict(
                        sorted(
                            self.interactions_data.items(),
                            key=lambda x: INTERACTION_ORDER.index(x[0]),
                        )
                    ).items()
                ]
            )
        else:
            interaction_types_detail_part = ""

        if self.max_interactions_date:
            max_interactions_count_day_part = (
                f"你互动量最多的一天是 {self.max_interactions_date.date()}，"
                f"这一天你在社区进行了 {self.max_interactions_count} 次互动。"
            )
        else:
            max_interactions_count_day_part = "在 2022 年中，你没有过互动行为。"

        if self.max_likes_user_name:
            max_likes_user_part = (
                f"你最喜欢给 {link(self.max_likes_user_name, self.max_likes_user_url, new_window=True)} 的文章点赞，"  # type: ignore
                f"这一年你为 TA 送上了 {self.max_likes_user_likes_count} 个赞。"
            )
        else:
            max_likes_user_part = "在 2022 年中，你没有点过赞。"

        if self.max_comments_user_name:
            max_comments_user_part = (
                f"你最喜欢评论 {link(self.max_comments_user_name, self.max_comments_user_url, new_window=True)} 的文章，"  # type: ignore
                f"这一年你在 TA 的文章下评论了 {self.max_comments_user_comments_count} 次。"
            )
        else:
            max_comments_user_part = "在 2022 年中，你没有发表过评论。"

        return "\n\n".join(
            [
                welcome_part,
                interaction_types_detail_part,
                max_interactions_count_day_part,
                max_likes_user_part,
                max_comments_user_part,
            ]
        )
