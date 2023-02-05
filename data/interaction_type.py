from typing import TYPE_CHECKING, Dict, List, Tuple

import pyecharts.options as opts
from bson import ObjectId
from pyecharts.charts import Pie
from pyecharts.globals import CurrentConfig

from data._base import DataModel
from utils.chart import (
    ANIMATION_OFF,
    NO_LEGEND,
    TOOLBOX_ONLY_SAVE_PNG_WHITE_2X,
)
from utils.config import config
from utils.constants import INTERACTION_NAME_MAPPING
from utils.db import interaction_type_db
from utils.dict_helper import get_reversed_dict

if TYPE_CHECKING:
    from data.user import User

CurrentConfig.ONLINE_HOST = config.deploy.PyEcharts_CDN


class InteractionType(DataModel):
    db = interaction_type_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "user_id": "user_id",
        "is_aviliable": "is_aviliable",
        "total_interactions_count": "total_interactions_count",
        "data": "data",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,  # noqa
        user_id: str,
        is_aviliable: bool,
        total_interactions_count: int,
        data: Dict[str, int],
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.is_aviliable = is_aviliable
        self.total_interactions_count = total_interactions_count
        self.data = data

        super().__init__()

    @classmethod
    def from_id(cls, id: str) -> "InteractionType":  # noqa
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @classmethod
    def from_user_id(cls, user_id: str) -> "InteractionType":
        db_data = cls.db.find_one({"user_id": user_id})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @property
    def user(self) -> User:
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def create(cls, user: User, data: Dict[str, int]) -> "InteractionType":
        insert_result = cls.db.insert_one(
            {
                "user_id": user.id,
                "is_aviliable": len(data) != 0,
                "total_interactions_count": sum(data.values()),
                "data": data,
            },
        )

        return cls.from_id(insert_result.inserted_id)

    def get_graph(self) -> Pie:
        # 对操作名称进行映射，如果找不到对应的文本，则返回原文本
        data_pair: List[Tuple[str, int]] = [
            (INTERACTION_NAME_MAPPING.get(name, name), value)
            for name, value in self.data.items()
        ]

        return (
            Pie(
                init_opts=opts.InitOpts(
                    width="880px",
                    height="600px",
                    animation_opts=ANIMATION_OFF,
                ),
            )
            .add(
                series_name="",
                data_pair=data_pair,
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    pos_left="30px",
                    pos_top="5px",
                    title=f"{self.user.name}的 2022 互动类型图",
                    subtitle=(f"总互动量：{self.total_interactions_count}"),
                ),
                legend_opts=NO_LEGEND,
                toolbox_opts=TOOLBOX_ONLY_SAVE_PNG_WHITE_2X,
            )
        )
