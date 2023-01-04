from datetime import datetime
from random import random
from time import sleep
from typing import Dict, Generator, List, Optional

from backoff import expo, on_exception
from httpx import TimeoutException
from JianshuResearchTools.user import GetUserTimelineInfo

from data.user import User, UserStatus
from utils.db import timeline_data_db
from utils.log import run_logger

STRAT_TIME: datetime = datetime(2022, 1, 1)
STOP_TIME: datetime = datetime(2022, 12, 31)

GetUserTimelineInfo = on_exception(
    expo,
    TimeoutException,
    base=2,
    factor=4,
    max_tries=5,
    on_backoff=lambda details: run_logger.warning(
        f"发生重试，尝试次数：{details['tries']}，等待时间：{round(details['wait'], 3)}"
    ),
)(GetUserTimelineInfo)


def get_all_data(user_url: str, start_id: Optional[int]) -> Generator[Dict, None, None]:
    max_id: int = start_id - 1 if start_id else 1000000000
    while True:
        data = GetUserTimelineInfo(user_url, max_id, disable_check=True)
        sleep(random())
        if not data:
            return

        for item in data:
            yield item

        max_id = data[-1]["operation_id"] - 1


def fetch_timeline_data(user: User) -> None:
    if user.status != UserStatus.WAITING:
        raise ValueError
    user.set_status_fetching()
    run_logger.debug(f"开始采集用户 {user.id} 的时间线数据")

    if user.fetch_start_id:
        run_logger.warning(f"用户 {user.id} 上次采集任务未完成，将从 {user.fetch_start_id} 处继续采集")

    buffer: List[Dict] = []
    for item in get_all_data(user.url, user.fetch_start_id):
        item["operation_time"] = item["operation_time"].replace(tzinfo=None)  # 处理时区问题
        if not STRAT_TIME < item["operation_time"] < STOP_TIME:
            continue  # 不在 2022 年内

        item["from_user"] = user.id
        item["fetch_time"] = datetime.now()

        buffer.append(item)

        if len(buffer) == 50:
            timeline_data_db.insert_many(buffer)
            buffer.clear()
            user.set_fetch_start_id(item["operation_id"])
            run_logger.debug(f"用户 {user.id} 的时间线数据已保存（{item['operation_id']}）")

    user.set_status_done()
    run_logger.debug(f"用户 {user.id} 的时间线数据采集已完成")
