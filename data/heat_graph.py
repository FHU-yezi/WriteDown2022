from datetime import datetime
from typing import Dict

import pyecharts.options as opts
from bson import ObjectId
from pyecharts.charts import Calendar
from pyecharts.globals import CurrentConfig

from data._base import DataModel
from utils.chart import (
    ANIMATION_OFF,
    CALENDAR_DAY_MONTH_CHINESE_YEAR_HIDE,
    TOOLBOX_ONLY_SAVE_PNG_WHITE_2X,
    VISUALMAP_JIANSHU_COLOR,
)
from utils.config import config
from utils.db import heat_graph_data_db
from utils.dict_helper import get_reversed_dict

CurrentConfig.ONLINE_HOST = config.deploy.PyEcharts_CDN


class HeatGraph(DataModel):
    db = heat_graph_data_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "user_id": "user_id",
        "max_interactions_count": "max_interactions_count",
        "total_active_days": "total_active_days",
        "total_interactions_count": "total_interactions_count",
        "data": "data",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,
        user_id: str,
        max_interactions_count: int,
        total_active_days: int,
        total_interactions_count: int,
        data: Dict[str, int],
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.max_interactions_count = max_interactions_count
        self.total_active_days = total_active_days
        self.total_interactions_count = total_interactions_count
        self.data = data

        super().__init__()

    @classmethod
    def from_id(cls, id: str) -> "HeatGraph":
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @classmethod
    def from_user_id(cls, user_id: str) -> "HeatGraph":
        db_data = cls.db.find_one({"user_id": user_id})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @property
    def user(self):
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def create(cls, user, data: Dict[str, int]) -> "HeatGraph":
        insert_result = cls.db.insert_one(
            {
                "user_id": user.id,
                "max_interactions_count": max(data.values()) if data else 0,
                "total_active_days": len(data),
                "total_interactions_count": sum(data.values()) if data else 0,
                "data": data,
            },
        )

        return cls.from_id(insert_result.inserted_id)

    def get_graph(self) -> Calendar:
        return (
            Calendar(
                init_opts=opts.InitOpts(
                    width="880px",
                    height="300px",
                    animation_opts=ANIMATION_OFF,
                ),
            )
            .add(
                series_name="",
                yaxis_data=[
                    (datetime.fromisoformat(key), value)
                    for key, value in self.data.items()
                ],
                calendar_opts=opts.CalendarOpts(
                    pos_left="5px",
                    pos_top="center",
                    range_="2022",
                    **CALENDAR_DAY_MONTH_CHINESE_YEAR_HIDE,
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    pos_left="30px",
                    pos_top="5px",
                    title=f"{self.user.name} 的 2022 互动热力图",
                    subtitle=(
                        f"活跃天数：{self.total_active_days}   "
                        f"活跃比例：{round(self.total_active_days / 365, 2) * 100}%   "
                        f"总互动量：{self.total_interactions_count}"
                    ),
                ),
                visualmap_opts=opts.VisualMapOpts(
                    pos_left="5px",
                    pos_bottom="5px",
                    min_=0,
                    # 数据范围会根据用户的最高单日互动量动态调整
                    # 数据范围上限为最高单日互动量十分位向上取整
                    # 如最高单日互动量为 123 时，数据范围上限为 130
                    max_=(int(self.max_interactions_count / 10) + 1) * 10,
                    orient="horizontal",
                    is_piecewise=True,
                    range_color=VISUALMAP_JIANSHU_COLOR,
                ),
                toolbox_opts=TOOLBOX_ONLY_SAVE_PNG_WHITE_2X,
            )
        )
