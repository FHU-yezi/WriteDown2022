from datetime import datetime
from random import random
from time import sleep
from typing import Dict, Generator, List, Optional

from backoff import expo, on_exception
from httpx import ConnectError, TimeoutException

from data.user import User
from utils.constants import DATA_STOP_TIME, DATA_STRAT_TIME, INTERACTION_ORDER
from utils.db import timeline_db
from utils.log import run_logger
from utils.timeline_fetcher import GetUserTimelineInfo

GetUserTimelineInfo = on_exception(
    expo,
    (TimeoutException, ConnectError),
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
        data = GetUserTimelineInfo(user_url, max_id)
        sleep(random())
        if not data:
            return

        for item in data:
            # 如果互动操作类型不在可分析的类型列表中，则不存储这条数据
            if item["operation_type"] not in INTERACTION_ORDER:
                continue
            yield item

        max_id = data[-1]["operation_id"] - 1


def fetch_timeline_data(user: User) -> None:
    if user.fetch_start_id:
        run_logger.warning(f"用户 {user.id} 上次采集任务未完成，将从 {user.fetch_start_id} 处继续采集")

    buffer: List[Dict] = []
    for item in get_all_data(user.url, user.fetch_start_id):
        operation_time = item["operation_time"].replace(tzinfo=None)
        item["operation_time"] = operation_time  # 处理时区问题

        if operation_time > DATA_STOP_TIME:
            continue  # 晚于 2022 年，尚未进入采集范围
        if operation_time < DATA_STRAT_TIME:
            break  # 早于 2022 年，已超出采集范围

        item["from_user"] = user.id
        item["fetch_time"] = datetime.now()

        buffer.append(item)
        if len(buffer) == 50:
            timeline_db.insert_many(buffer)
            buffer.clear()
            user.set_fetch_start_id(item["operation_id"])
            run_logger.debug(f"已保存用户 {user.id} 的时间线数据（{item['operation_id']}）")

    # 采集完成，将剩余数据存入数据库
    if buffer:
        timeline_db.insert_many(buffer)
        buffer.clear()
        user.set_fetch_start_id(item["operation_id"])
        run_logger.debug(f"已保存用户 {user.id} 的时间线数据（{item['operation_id']}）")
