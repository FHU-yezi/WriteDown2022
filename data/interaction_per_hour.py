from typing import Dict

import pyecharts.options as opts
from bson import ObjectId
from pyecharts.charts import Line
from pyecharts.globals import CurrentConfig

from data._base import DataModel
from utils.chart import (
    ANIMATION_OFF,
    JIANSHU_COLOR,
    NO_LEGEND,
    TOOLBOX_ONLY_SAVE_PNG_WHITE_2X,
)
from utils.config import config
from utils.db import interaction_per_hour_db
from utils.dict_helper import get_reversed_dict

CurrentConfig.ONLINE_HOST = config.deploy.PyEcharts_CDN


class InteractionPerHour(DataModel):
    db = interaction_per_hour_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "user_id": "user_id",
        "data": "data",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(self, id: str, user_id: str, data: Dict[str, int]) -> None:
        self.id = id
        self.user_id = user_id
        self.data = data

        super().__init__()

    @classmethod
    def from_id(cls, id: str) -> "InteractionPerHour":
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @classmethod
    def from_user_id(cls, user_id: str) -> "InteractionPerHour":
        db_data = cls.db.find_one({"user_id": user_id})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @property
    def user(self):
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def create(cls, user, data: Dict[str, int]) -> "InteractionPerHour":
        insert_result = cls.db.insert_one(
            {
                "user_id": user.id,
                "data": data,
            },
        )

        return cls.from_id(insert_result.inserted_id)

    def get_graph(self) -> Line:
        return (
            Line(
                init_opts=opts.InitOpts(
                    width="880px",
                    height="450px",
                    animation_opts=ANIMATION_OFF,
                ),
            )
            .add_xaxis(
                tuple(self.data.keys()),
            )
            .add_yaxis(
                "",
                y_axis=tuple(self.data.values()),
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(
                    color=JIANSHU_COLOR,
                ),
                label_opts=opts.LabelOpts(
                    color=JIANSHU_COLOR,
                ),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JIANSHU_COLOR,
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    pos_left="30px",
                    pos_top="5px",
                    title=f"{self.user.name}的 2022 互动小时分布图",
                ),
                xaxis_opts=opts.AxisOpts(
                    name="小时"
                ),
                yaxis_opts=opts.AxisOpts(
                    name="互动次数"
                ),
                legend_opts=NO_LEGEND,
                toolbox_opts=TOOLBOX_ONLY_SAVE_PNG_WHITE_2X,
            )
        )
