from typing import TYPE_CHECKING, Dict

import pyecharts.options as opts
from bson import ObjectId
from pyecharts.charts import WordCloud as _WordCloud
from pyecharts.globals import CurrentConfig

from data._base import DataModel
from utils.chart import JIANSHU_COLOR, TOOLBOX_ONLY_SAVE_PNG_WHITE_2X
from utils.config import config
from utils.db import wordcloud_db
from utils.dict_helper import get_reversed_dict

if TYPE_CHECKING:
    from data.user import User

CurrentConfig.ONLINE_HOST = config.deploy.PyEcharts_CDN


class Wordcloud(DataModel):
    db = wordcloud_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "user_id": "user_id",
        "is_aviliable": "is_aviliable",
        "total_comments_count": "total_comments_count",
        "data": "data",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,  # noqa
        user_id: str,
        is_aviliable: bool,
        total_comments_count: int,
        data: Dict[str, str],
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.is_aviliable = is_aviliable
        self.total_comments_count = total_comments_count
        self.data = data

        super().__init__()

    @classmethod
    def from_id(cls, id: str) -> "Wordcloud":  # noqa
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @classmethod
    def from_user_id(cls, user_id: str) -> "Wordcloud":
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
        cls, user: User, data: Dict[str, int], total_comments_count: int
    ) -> "Wordcloud":
        insert_result = cls.db.insert_one(
            {
                "user_id": user.id,
                "is_aviliable": len(data) != 0,
                "total_comments_count": total_comments_count,
                "data": data,
            },
        )

        return cls.from_id(insert_result.inserted_id)

    def get_graph(self) -> _WordCloud:
        return (
            _WordCloud(
                init_opts=opts.InitOpts(
                    width="880px",
                    height="500px",
                    animation_opts=opts.AnimationOpts(
                        animation=False,
                    ),
                ),
            )
            .add(
                series_name="",
                data_pair=tuple(self.data.items()),
                word_size_range=[10, 70],
                pos_left="center",
                pos_top="center",
                textstyle_opts=opts.TextStyleOpts(color=JIANSHU_COLOR),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    pos_left="30px",
                    pos_top="5px",
                    title=f"{self.user.name}的 2022 评论词云图",
                    subtitle=f"总评论量：{self.total_comments_count}",
                ),
                toolbox_opts=TOOLBOX_ONLY_SAVE_PNG_WHITE_2X,
            )
        )
