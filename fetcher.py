from datetime import datetime
from random import randint
from time import sleep
from typing import Any, Dict, Generator, List, Optional

from JianshuResearchTools.user import GetUserTimelineInfo

from data.user import User
from utils.config import config
from utils.constants import DATA_STOP_TIME, DATA_STRAT_TIME, INTERACTION_ORDER
from utils.db import timeline_db
from utils.log import run_logger
from utils.retry import retry_on_network_error

GetUserTimelineInfo = retry_on_network_error(GetUserTimelineInfo)


def get_all_data(
    user_url: str, start_id: Optional[int]
) -> Generator[Dict[str, Any], None, None]:
    max_id: int = start_id - 1 if start_id else 1000000000
    while True:
        data = GetUserTimelineInfo(user_url, max_id)
        # 在配置文件指定的范围内随机 sleep 一段时间
        sleep(
            randint(  # noqa: S311
                config.fetcher.sleep_interval_low,
                config.fetcher.sleep_interval_high,
            )
            / 1000
        )
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
        user.set_fetch_start_id(item["operation_id"])  # type: ignore
        run_logger.debug(
            f"已保存用户 {user.id} 的时间线数据（{item['operation_id']}）",  # type: ignore
        )
