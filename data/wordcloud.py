from typing import Dict

import pyecharts.options as opts
from bson import ObjectId
from pyecharts.charts import WordCloud as _WordCloud

from data._base import DataModel
from utils.db import wordcloud_data_db
from utils.dict_helper import get_reversed_dict


class Wordcloud(DataModel):
    db = wordcloud_data_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "user_id": "user_id",
        "data": "data",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(self, id: str, user_id: str, data: Dict[str, str]) -> None:
        self.id = id
        self.user_id = user_id
        self.data = data

        super().__init__()

    @classmethod
    def from_id(cls, id: str) -> "Wordcloud":
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data)

    @property
    def user(self):
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def create(cls, user, data: Dict[str, int]) -> "Wordcloud":
        insert_result = cls.db.insert_one(
            {
                "user_id": user.id,
                "data": data,
            },
        )

        return cls.from_id(insert_result.inserted_id)

    def get_graph_obj(self, width: int, height: int) -> _WordCloud:
        return (
            _WordCloud(
                init_opts=opts.InitOpts(
                    width=width,
                    height=height,
                ),
            )
            .add(
                series_name="",
                data_pair=tuple(self.data.items()),
                word_size_range=[10, 70],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"{self.user.name} 的 2022 评论词云图",
                ),
            )
        )
