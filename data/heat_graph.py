from typing import Dict

import pyecharts.options as opts
from bson import ObjectId
from pyecharts.charts import Calendar

from data._base import DataModel
from utils.db import heat_graph_data_db
from utils.dict_helper import get_reversed_dict


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
        return cls.from_db_data(db_data)

    @property
    def user(self):
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def create(cls, user, data: Dict[str, int]) -> "HeatGraph":
        insert_result = cls.db.insert_one(
            {
                "user_id": user.id,
                "max_ineractions_count": max(data.values()),
                "total_active_days": len(data),
                "total_interactions_count": sum(data.values()),
                "data": data,
            },
        )

        return cls.from_id(insert_result.inserted_id)

    def get_graph_obj(self, width: int, height: int) -> Calendar:
        return (
            Calendar(
                init_opts=opts.InitOpts(
                    width=width,
                    height=height,
                ),
            )
            .add(
                series_name="",
                yaxis_data=list(self.data.items()),
                calendar_opts=opts.CalendarOpts(
                    range_="2022",
                    daylabel_opts=opts.CalendarDayLabelOpts(
                        name_map="cn",
                    ),
                    monthlabel_opts=opts.CalendarMonthLabelOpts(
                        name_map="cn",
                    ),
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    pos_left="center",
                    title=f"{self.user.name} 的 2022 互动热力图",
                    subtitle=(
                        f"活跃天数：{self.total_active_days} "
                        f"/ 总互动量：{self.total_interactions_count}"
                    ),
                ),
                visualmap_opts=opts.VisualMapOpts(
                    min_=0,
                    # 数据范围会根据用户的最高单日互动量动态调整
                    # 数据范围上限为最高单日互动量十分位向上取整
                    # 如最高单日互动量为 123 时，数据范围上限为 130
                    max_=(int(self.max_interactions_count / 10) + 1) * 10,
                    orient="horizontal",
                    is_piecewise=True,
                ),
            )
        )
