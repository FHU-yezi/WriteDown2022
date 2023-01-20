from typing import Any, Dict, List, Optional

from bson import ObjectId

from data._base import DataModel
from utils.db import on_rank_db
from utils.dict_helper import get_reversed_dict
from utils.html import grey_text, link


class OnRank(DataModel):
    db = on_rank_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "user_id": "user_id",
        "is_aviliable": "is_aviliable",
        "on_rank_count": "on_rank_count",
        "top_ranking": "top_ranking",
        "articles_data": "articles_data",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,
        user_id: str,
        is_aviliable: bool,
        on_rank_count: int,
        top_ranking: Optional[int],
        articles_data: Optional[Dict[str, Any]],
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.is_aviliable = is_aviliable
        self.on_rank_count = on_rank_count
        self.top_ranking = top_ranking
        self.articles_data = articles_data

        super().__init__()

    @classmethod
    def from_id(cls, id: str) -> "OnRank":
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @classmethod
    def from_user_id(cls, user_id: str) -> "OnRank":
        db_data = cls.db.find_one({"user_id": user_id})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @property
    def user(self):
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def create(
        cls,
        user,
        on_rank_count: int,
        top_ranking: Optional[int],
        articles_data: Optional[List[Dict[str, Any]]],
    ) -> "OnRank":
        insert_result = cls.db.insert_one(
            {
                "user_id": user.id,
                "is_aviliable": True,
                "on_rank_count": on_rank_count,
                "top_ranking": top_ranking,
                "articles_data": articles_data,
            },
        )

        return cls.from_id(insert_result.inserted_id)

    def get_report(self) -> str:
        if not self.on_rank_count:
            return "在 2022 年，你的文章没有上过收益排行榜。"

        summary_part = (
            f"在 2022 年，你写的文章曾 {self.on_rank_count} 次登上收益排行榜，"
            f"最高排名第 {self.top_ranking} 名。"
        )

        if self.on_rank_count > len(self.articles_data):
            before_detail = "以下是你的部分上榜记录："
        else:
            before_detail = "以下是你的上榜记录："

        on_rank_detail = "- " + "\n- ".join(
            [
                (
                    f"{item['date'].month} 月 {item['date'].day} 日，"
                    f"文章 {link(item['article_title'], item['article_url'], new_window=True)} "
                    f"登上排行榜第 {item['ranking']} 名"
                )
                # article_data 在分析阶段保证有序，此处不再进行排序
                for item in self.articles_data
            ],
        )

        on_rank_search_tool_ad = grey_text(
            f"（查看上榜详情请点击访问 "
            f"{link('上榜文章查询工具', 'https://tools.sscreator.com/?app=on_rank_article_viewer', new_window=True)}）"
        )

        return "\n\n".join(
            [
                summary_part,
                before_detail,
                on_rank_detail,
                on_rank_search_tool_ad,
            ]
        )
