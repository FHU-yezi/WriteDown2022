from datetime import datetime
from threading import Thread
from time import sleep
from typing import List

from analyzer import analyze_active_data, analyze_comment_word_freq
from data.user import UserStatus, get_waiting_user
from fetcher import fetch_timeline_data
from utils.config import config
from utils.db import user_data_db
from utils.log import run_logger


def queue_processor_thread() -> None:
    while True:
        user = get_waiting_user()
        if not user:
            sleep(config.queue_processor.check_interval)
            run_logger.debug(f"队列为空，{config.queue_processor.check_interval} 秒后再次查询")
            continue

        try:
            fetch_timeline_data(user)
        except Exception as e:
            user.set_status_error("获取时间线数据失败")
            run_logger.error(f"获取用户 {user.id} 的时间线数据时发生异常：{repr(e)}")
            continue

        try:
            analyze_active_data(user)
        except Exception as e:
            user.set_status_error("分析活跃度数据失败")
            run_logger.error(f"分析 {user.id} 的活跃度数据时发生异常：{repr(e)}")
            continue

        try:
            analyze_comment_word_freq(user)
        except Exception as e:
            user.set_status_error("分析评论词频失败")
            run_logger.error(f"分析 {user.id} 的评论词频数据时发生异常：{repr(e)}")
            continue


def clean_unfinished_job() -> None:
    cleaned_count = user_data_db.update_many(
        {
            "status": UserStatus.FETCHING,
        },
        {
            "$set": {
                "status": UserStatus.WAITING,
                "timestamp.start_fetch": datetime.now(),
            }
        },
    ).modified_count
    if cleaned_count:
        run_logger.warning(f"有 {cleaned_count} 个未完成的任务，已重新加入队列")
    else:
        run_logger.info("没有未完成的任务")


def start_queue_processor_threads() -> List[Thread]:
    threads_list: List[Thread] = []

    run_logger.debug(f"将启动 {config.queue_processor.threads} 个队列处理线程")
    for i in range(config.queue_processor.threads):
        thread = Thread(
            target=queue_processor_thread,
            name=f"queue-processor-{i}",
            daemon=True,
        )
        thread.start()
        threads_list.append(thread)

    return threads_list
