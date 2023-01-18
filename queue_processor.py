from threading import Thread
from time import sleep
from typing import List

from analyzers import ANALYZE_FUNCS
from data.user import UserStatus, get_waiting_user
from fetcher import fetch_timeline_data
from utils.config import config
from utils.db import user_db
from utils.log import run_logger


def queue_processor_thread(start_sleep_time: int) -> None:
    sleep(start_sleep_time)

    while True:
        user = get_waiting_user()
        if not user:
            sleep(config.queue_processor.check_interval)
            continue

        user.set_status_fetching()
        run_logger.debug(f"开始采集用户 {user.id} 的时间线数据")
        try:
            fetch_timeline_data(user)
        except Exception as e:
            user.set_status_fetch_error("获取时间线数据失败")
            run_logger.error(f"获取用户 {user.id} 的时间线数据时发生异常：{repr(e)}")
            continue
        else:
            user.set_status_waiting_for_analyze()
            run_logger.debug(f"用户 {user.id} 的时间线数据采集已完成")

        user.set_status_analyzing()
        for analyze_item_name, analyze_func in ANALYZE_FUNCS.items():
            try:
                analyze_func(user)
            except Exception as e:
                user.set_status_analyze_error(f"分析{analyze_item_name}失败")
                run_logger.error(f"分析 {user.id} 的{analyze_item_name}时发生异常：{repr(e)}")
                break
            else:
                user.set_status_analyze_done()
                run_logger.debug(f"已完成对 {user.id} 的{analyze_item_name}分析")

        run_logger.debug(f"已完成对 {user.id} 的全部处理流程")


def clean_unfinished_job() -> None:
    cleaned_count = user_db.update_many(
        {
            "status": UserStatus.FETCHING,
        },
        {
            "$set": {
                "status": UserStatus.WAITING_FOR_FETCH,
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
            kwargs={
                "start_sleep_time": config.queue_processor.check_interval
                / config.queue_processor.threads
                * (i + 1)
            },
        )
        thread.start()
        threads_list.append(thread)

    return threads_list
