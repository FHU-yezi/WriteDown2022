from datetime import datetime
from typing import Any, Dict, List

import pyecharts.options as opts
from bson import ObjectId
from pyecharts.charts import Calendar
from pyecharts.globals import CurrentConfig

from data._base import DataModel
from utils.chart import (
    ANIMATION_OFF,
    CALENDAR_MONTH_CHINESE_DAY_YEAR_HIDE,
    TOOLBOX_ONLY_SAVE_PNG_WHITE_2X,
    VISUALMAP_JIANSHU_COLOR,
)
from utils.config import config
from utils.db import general_data_db
from utils.dict_helper import get_reversed_dict

CurrentConfig.ONLINE_HOST = config.deploy.PyEcharts_CDN


class GeneralData(DataModel):
    db = general_data_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "analyze_time": "analyze_time",
        "total_users_count": "total_users_count",
        "active_data": "active_data",
        "min_interactions_count": "min_interactions_count",
        "max_interactions_count": "max_interactions_count",
        "total_interactions_count": "total_interactions_count",
        "popular_users_data": "popular_users_data",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,  # noqa
        analyze_time: datetime,
        total_users_count: int,
        active_data: Dict[str, int],
        min_interactions_count: int,
        max_interactions_count: int,
        total_interactions_count: int,
        popular_users_data: List[Dict[str, Any]],
    ) -> None:
        self.id = id
        self.analyze_time = analyze_time
        self.total_users_count = total_users_count
        self.active_data = active_data
        self.min_interactions_count = min_interactions_count
        self.max_interactions_count = max_interactions_count
        self.total_interactions_count = total_interactions_count
        self.popular_users_data = popular_users_data

        super().__init__()

    @classmethod
    def from_id(cls, id: str) -> "GeneralData":  # noqa
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @classmethod
    def get_latest(cls) -> "GeneralData":
        # 聚合分析数据库只会有一条数据
        db_data = cls.db.find_one()
        if not db_data:
            raise ValueError
        return cls.from_db_data(db_data, flatten=False)

    @classmethod
    def create(
        cls,
        total_users_count: int,
        active_data: Dict[str, int],
        popular_users_data: List[Dict[str, Any]],
    ) -> "GeneralData":
        insert_result = cls.db.insert_one(
            {
                "analyze_time": datetime.now(),
                "total_users_count": total_users_count,
                "active_data": active_data,
                "min_interactions_count": min(active_data.values()),
                "max_interactions_count": max(active_data.values()),
                "total_interactions_count": sum(active_data.values()),
                "popular_users_data": popular_users_data,
            },
        )

        return cls.from_id(insert_result.inserted_id)

    def get_active_graph(self) -> Calendar:
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
                    for key, value in self.active_data.items()
                ],
                calendar_opts=opts.CalendarOpts(
                    pos_left="5px",
                    pos_right="5px",
                    pos_top="center",
                    range_="2022",
                    **CALENDAR_MONTH_CHINESE_DAY_YEAR_HIDE,
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    pos_left="30px",
                    pos_top="5px",
                    title="「落格」2022 互动热力图",
                    subtitle=(
                        f"总互动量：{self.total_interactions_count}"
                    ),
                ),
                visualmap_opts=opts.VisualMapOpts(
                    pos_left="5px",
                    pos_bottom="5px",
                    # 数据范围会根据单日互动量动态调整
                    # 数据范围上限为单日互动量百分位向上 / 下取整
                    # 如最高单日互动量为 123 时，数据范围上限为 130
                    min_=(int(self.min_interactions_count / 100) - 1) * 100,
                    max_=(int(self.max_interactions_count / 100) + 1) * 100,
                    orient="horizontal",
                    is_piecewise=True,
                    range_color=VISUALMAP_JIANSHU_COLOR,
                ),
                toolbox_opts=TOOLBOX_ONLY_SAVE_PNG_WHITE_2X,
            )
        )
